import logging
import uuid
from typing import Any
from uuid import UUID

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Request, Response, UploadFile

import repository
from db import Conn, DbConn, write_transaction
from errors import ConflictProblem, UnavailableProblem, ValidationProblem, require
from schemas import Plot, PlotArea, PlotCreate, PlotPhoto, PlotUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/plots", tags=["plots"])

M2_PER_DUNAM = 1000

PHOTO_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
PHOTO_MAX_BYTES = 5 * 1024 * 1024
PHOTO_UNAVAILABLE = "Photo storage is unavailable; retry later"

# Reference field -> (noun for messages, lookup that proves the referenced record exists).
_REFERENCES = {
    "farm_id": ("farm", repository.get_farm),
    "crop_id": ("crop", repository.get_crop),
    "soil_id": ("soil", repository.get_soil),
    "emitter_id": ("emitter", repository.get_emitter),
}


@router.post("", status_code=201, response_model=Plot)
def create_plot(body: PlotCreate, conn: DbConn) -> dict[str, Any]:
    plot = {"id": str(uuid.uuid4()), **body.model_dump(mode="json")}
    with write_transaction(conn):
        _check_references(conn, plot)
        _check_name_free(conn, plot["farm_id"], plot["name"], plot_id=None)
        repository.insert_plot(conn, plot)
    return plot


@router.get("", response_model=list[Plot])
def list_plots(conn: DbConn, farm_id: UUID | None = None) -> list[dict[str, Any]]:
    return repository.list_plots(conn, None if farm_id is None else str(farm_id))


@router.get("/{plot_id}", response_model=Plot)
def get_plot(plot_id: UUID, conn: DbConn) -> dict[str, Any]:
    return _plot_or_404(conn, plot_id)


@router.get("/{plot_id}/area", response_model=PlotArea)
def get_plot_area(plot_id: UUID, conn: DbConn) -> dict[str, Any]:
    plot = _plot_or_404(conn, plot_id)
    return {
        "plot_id": plot["id"],
        "area_m2": plot["area_m2"],
        "area_dunam": plot["area_m2"] / M2_PER_DUNAM,
    }


# Sync handlers like the rest: FastAPI runs them in a thread pool, so the blocking DB and S3
# calls do not hold up the event loop.
@router.post("/{plot_id}/photo", status_code=201, response_model=PlotPhoto)
def upload_plot_photo(
    plot_id: UUID, file: UploadFile, request: Request, conn: DbConn
) -> dict[str, Any]:
    if file.content_type not in PHOTO_CONTENT_TYPES:
        raise ValidationProblem(
            f"file: content type must be one of {', '.join(sorted(PHOTO_CONTENT_TYPES))}"
        )
    # Read one byte past the limit, so an oversized file is caught without reading all of it.
    data = file.file.read(PHOTO_MAX_BYTES + 1)
    if not data:
        raise ValidationProblem("file: must not be empty")
    if len(data) > PHOTO_MAX_BYTES:
        raise ValidationProblem(f"file: must be at most {PHOTO_MAX_BYTES} bytes")

    plot = _plot_or_404(conn, plot_id)
    key = f"{plot['farm_id']}/{plot['id']}/photo"
    bucket = _photo_bucket(request)
    try:
        _s3_client(request).put_object(
            Bucket=bucket, Key=key, Body=data, ContentType=file.content_type
        )
    except (BotoCoreError, ClientError) as exc:
        logger.error("S3 upload failed for plot %s", plot_id, exc_info=exc)
        raise UnavailableProblem(PHOTO_UNAVAILABLE) from exc

    with write_transaction(conn):
        # The plot may have been deleted while the upload ran.
        _plot_or_404(conn, plot_id)
        repository.upsert_plot_photo(conn, str(plot_id), key, file.content_type)
    return {"plot_id": plot_id, "key": key, "content_type": file.content_type}


@router.get("/{plot_id}/photo", response_class=Response)
def get_plot_photo(plot_id: UUID, request: Request, conn: DbConn) -> Response:
    _plot_or_404(conn, plot_id)
    photo = require(repository.get_plot_photo(conn, str(plot_id)), f"Plot {plot_id} has no photo")
    bucket = _photo_bucket(request)
    try:
        response = _s3_client(request).get_object(Bucket=bucket, Key=photo["key"])
        with response["Body"] as body:
            data = body.read()
    except (BotoCoreError, ClientError) as exc:
        logger.error("S3 download failed for plot %s", plot_id, exc_info=exc)
        raise UnavailableProblem(PHOTO_UNAVAILABLE) from exc
    return Response(content=data, media_type=photo["content_type"])


@router.patch("/{plot_id}", response_model=Plot)
def update_plot(plot_id: UUID, body: PlotUpdate, conn: DbConn) -> dict[str, Any]:
    changes = body.model_dump(mode="json", exclude_unset=True)
    with write_transaction(conn):
        current = _plot_or_404(conn, plot_id)
        _check_references(conn, changes)
        _check_name_free(
            conn,
            changes.get("farm_id", current["farm_id"]),
            changes.get("name", current["name"]),
            plot_id=str(plot_id),
        )
        repository.update_plot(conn, str(plot_id), changes)
        return _plot_or_404(conn, plot_id)


@router.delete("/{plot_id}", status_code=204)
def delete_plot(plot_id: UUID, conn: DbConn) -> Response:
    with write_transaction(conn):
        _plot_or_404(conn, plot_id)
        repository.delete_plot(conn, str(plot_id))
    return Response(status_code=204)


def _plot_or_404(conn: Conn, plot_id: UUID) -> dict[str, Any]:
    return require(repository.get_plot(conn, str(plot_id)), f"Plot {plot_id} not found")


def _photo_bucket(request: Request) -> str:
    bucket = request.app.state.s3_bucket
    if not bucket:
        logger.error("AWS_S3_BUCKET is not set; plot photos are unavailable")
        raise UnavailableProblem(PHOTO_UNAVAILABLE)
    return bucket


def _s3_client(request: Request) -> Any:
    # Created per request, never at import. No credentials here: boto3 finds them itself.
    return boto3.client("s3", region_name=request.app.state.aws_region)


def _check_references(conn: Conn, values: dict[str, Any]) -> None:
    problems = [
        f"{field}: unknown {noun} {values[field]!r}"
        for field, (noun, lookup) in _REFERENCES.items()
        if field in values and lookup(conn, values[field]) is None
    ]
    if problems:
        raise ValidationProblem("; ".join(problems))


def _check_name_free(conn: Conn, farm_id: str, name: str, plot_id: str | None) -> None:
    if repository.plot_name_taken(conn, farm_id, name, plot_id):
        raise ConflictProblem(f"A plot named {name!r} already exists on this farm")

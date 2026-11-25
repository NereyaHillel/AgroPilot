import io
from pathlib import Path

import boto3
import pytest
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError
from fastapi.testclient import TestClient
from support import FARM_DEMO, FARM_EAST, PLOT_EAST, PLOT_NORTH, UNKNOWN_ID, database_from
from test_errors import assert_problem

import repository
from db import connect_url, get_db
from main import app

BUCKET = "test-bucket"
REGION = "eu-north-1"
NORTH_KEY = f"{FARM_DEMO}/{PLOT_NORTH}/photo"
JPEG = b"\xff\xd8\xff\xe0 fake jpeg bytes"
PNG = b"\x89PNG\r\n\x1a\n fake png bytes"
MAX_BYTES = 5 * 1024 * 1024


class FakeS3:
    """Stands in for boto3's S3 client: keeps objects in memory and records every call."""

    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], tuple[bytes, str]] = {}
        self.calls: list[str] = []
        self.client_kwargs: list[dict] = []
        self.error: Exception | None = None
        self.before_put = None

    def client(self, service: str, **kwargs):
        assert service == "s3"
        self.client_kwargs.append(kwargs)
        return self

    def put_object(self, *, Bucket, Key, Body, ContentType):
        self.calls.append("put_object")
        if self.before_put:
            self.before_put()
        if self.error:
            raise self.error
        self.objects[(Bucket, Key)] = (Body, ContentType)

    def get_object(self, *, Bucket, Key):
        self.calls.append("get_object")
        if self.error:
            raise self.error
        return {"Body": io.BytesIO(self.objects[(Bucket, Key)][0])}


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> FakeS3:
    fake = FakeS3()
    monkeypatch.setattr(boto3, "client", fake.client)
    # TestClient is not entered as a context manager, so lifespan never sets these.
    monkeypatch.setattr(app.state, "s3_bucket", BUCKET, raising=False)
    monkeypatch.setattr(app.state, "aws_region", REGION, raising=False)
    return fake


def upload(client: TestClient, data: bytes, content_type: str, plot_id: str = PLOT_NORTH):
    return client.post(f"/v1/plots/{plot_id}/photo", files={"file": ("photo", data, content_type)})


def stored_row(db_url: str, plot_id: str = PLOT_NORTH):
    with connect_url(db_url) as conn:
        return repository.get_plot_photo(conn, plot_id)


# --- success -----------------------------------------------------------------------------


@pytest.mark.parametrize("content_type", ["image/jpeg", "image/png", "image/webp"])
def test_upload_returns_201_with_only_spec_fields(client, s3, content_type):
    response = upload(client, JPEG, content_type)

    assert response.status_code == 201
    assert response.json() == {"plot_id": PLOT_NORTH, "key": NORTH_KEY, "content_type": content_type}


def test_upload_stores_object_under_farm_and_plot_key(client, s3, db_url):
    upload(client, JPEG, "image/jpeg")

    assert s3.objects == {(BUCKET, NORTH_KEY): (JPEG, "image/jpeg")}
    assert stored_row(db_url) == {"key": NORTH_KEY, "content_type": "image/jpeg"}


def test_s3_client_uses_configured_region_and_no_credentials(client, s3):
    upload(client, JPEG, "image/jpeg")
    client.get(f"/v1/plots/{PLOT_NORTH}/photo")

    assert s3.client_kwargs == [{"region_name": REGION}, {"region_name": REGION}]


def test_get_returns_uploaded_bytes_with_content_type(client, s3):
    upload(client, PNG, "image/png")

    response = client.get(f"/v1/plots/{PLOT_NORTH}/photo")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == PNG


def test_second_upload_overwrites_object_and_row(client, s3, db_url):
    upload(client, JPEG, "image/jpeg")
    response = upload(client, PNG, "image/png")

    assert response.status_code == 201
    assert s3.objects == {(BUCKET, NORTH_KEY): (PNG, "image/png")}
    assert stored_row(db_url) == {"key": NORTH_KEY, "content_type": "image/png"}
    assert client.get(f"/v1/plots/{PLOT_NORTH}/photo").content == PNG


def test_file_of_exactly_5_mb_is_accepted(client, s3):
    assert upload(client, b"x" * MAX_BYTES, "image/jpeg").status_code == 201


def test_key_uses_plot_current_farm(client, s3):
    client.patch(f"/v1/plots/{PLOT_NORTH}", json={"farm_id": FARM_EAST})

    response = upload(client, JPEG, "image/jpeg")

    assert response.json()["key"] == f"{FARM_EAST}/{PLOT_NORTH}/photo"


def test_get_uses_stored_key_after_plot_moves_farm(client, s3):
    upload(client, JPEG, "image/jpeg")
    client.patch(f"/v1/plots/{PLOT_NORTH}", json={"farm_id": FARM_EAST})

    response = client.get(f"/v1/plots/{PLOT_NORTH}/photo")

    assert response.status_code == 200
    assert response.content == JPEG


def test_plot_json_has_no_photo_fields(client, s3):
    before = client.get(f"/v1/plots/{PLOT_NORTH}").json()
    upload(client, JPEG, "image/jpeg")

    assert client.get(f"/v1/plots/{PLOT_NORTH}").json() == before


def test_deleting_plot_removes_its_photo_row(client, s3, db_url):
    upload(client, JPEG, "image/jpeg")

    assert client.delete(f"/v1/plots/{PLOT_NORTH}").status_code == 204
    assert stored_row(db_url) is None


# --- 404 -----------------------------------------------------------------------------------


def test_upload_to_unknown_plot_returns_404_without_s3(client, s3):
    assert_problem(upload(client, JPEG, "image/jpeg", plot_id=UNKNOWN_ID), 404, "NOT_FOUND")
    assert s3.calls == []


def test_get_photo_of_unknown_plot_returns_404(client, s3):
    assert_problem(client.get(f"/v1/plots/{UNKNOWN_ID}/photo"), 404, "NOT_FOUND")
    assert s3.calls == []


def test_get_photo_before_upload_returns_404(client, s3):
    assert_problem(client.get(f"/v1/plots/{PLOT_EAST}/photo"), 404, "NOT_FOUND")
    assert s3.calls == []


def test_plot_deleted_during_upload_returns_404(client, s3, db_url):
    def delete_plot() -> None:
        with connect_url(db_url) as conn:
            repository.delete_plot(conn, PLOT_NORTH)

    s3.before_put = delete_plot

    assert_problem(upload(client, JPEG, "image/jpeg"), 404, "NOT_FOUND")
    assert stored_row(db_url) is None


# --- 422 -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("data", "content_type"),
    [
        (b"", "image/jpeg"),
        (JPEG, "image/gif"),
        (JPEG, "text/plain"),
        (JPEG, "application/octet-stream"),
        (b"x" * (MAX_BYTES + 1), "image/jpeg"),
    ],
    ids=["empty", "gif", "text", "octet-stream", "over-5-mb"],
)
def test_invalid_file_returns_422_without_s3(client, s3, db_url, data, content_type):
    assert_problem(upload(client, data, content_type), 422, "VALIDATION")
    assert s3.calls == []
    assert stored_row(db_url) is None


def test_missing_file_field_returns_422(client, s3):
    response = client.post(
        f"/v1/plots/{PLOT_NORTH}/photo", files={"other": ("photo", JPEG, "image/jpeg")}
    )

    assert_problem(response, 422, "VALIDATION")
    assert s3.calls == []


@pytest.mark.parametrize("method", ["get", "post"])
def test_malformed_plot_id_returns_422(client, s3, method):
    kwargs = {"files": {"file": ("photo", JPEG, "image/jpeg")}} if method == "post" else {}

    response = getattr(client, method)("/v1/plots/not-a-uuid/photo", **kwargs)

    assert_problem(response, 422, "VALIDATION")
    assert s3.calls == []


# --- 503 -----------------------------------------------------------------------------------

S3_ERRORS = [
    ClientError({"Error": {"Code": "AccessDenied", "Message": "denied"}}, "PutObject"),
    ClientError({"Error": {"Code": "NoSuchKey", "Message": "gone"}}, "GetObject"),
    NoCredentialsError(),
    EndpointConnectionError(endpoint_url="https://s3.example"),
]
S3_ERROR_IDS = ["access-denied", "no-such-key", "no-credentials", "endpoint"]


@pytest.mark.parametrize("error", S3_ERRORS, ids=S3_ERROR_IDS)
def test_s3_error_on_upload_returns_503_and_keeps_stored_key(client, s3, db_url, error, caplog):
    upload(client, JPEG, "image/jpeg")
    s3.error = error

    response = upload(client, PNG, "image/png")

    assert_problem(response, 503, "UNAVAILABLE")
    assert response.headers["retry-after"] == "5"
    assert stored_row(db_url) == {"key": NORTH_KEY, "content_type": "image/jpeg"}
    assert "S3 upload failed" in caplog.text


def test_s3_error_on_first_upload_stores_nothing(client, s3, db_url):
    s3.error = NoCredentialsError()

    assert_problem(upload(client, JPEG, "image/jpeg"), 503, "UNAVAILABLE")
    assert stored_row(db_url) is None


@pytest.mark.parametrize("error", S3_ERRORS, ids=S3_ERROR_IDS)
def test_s3_error_on_download_returns_503(client, s3, error, caplog):
    upload(client, JPEG, "image/jpeg")
    s3.error = error

    response = client.get(f"/v1/plots/{PLOT_NORTH}/photo")

    assert_problem(response, 503, "UNAVAILABLE")
    assert response.headers["retry-after"] == "5"
    assert "S3 download failed" in caplog.text


def test_s3_client_creation_error_returns_503(client, s3, monkeypatch):
    def broken_client(service: str, **kwargs):
        raise NoCredentialsError()

    monkeypatch.setattr(boto3, "client", broken_client)

    assert_problem(upload(client, JPEG, "image/jpeg"), 503, "UNAVAILABLE")


@pytest.mark.parametrize("method", ["get", "post"])
def test_unset_bucket_returns_503_without_s3(client, s3, db_url, method, caplog):
    with connect_url(db_url) as conn:
        repository.upsert_plot_photo(conn, PLOT_NORTH, NORTH_KEY, "image/jpeg")
    app.state.s3_bucket = ""  # the s3 fixture removes it again after the test
    kwargs = {"files": {"file": ("photo", PNG, "image/png")}} if method == "post" else {}

    response = getattr(client, method)(f"/v1/plots/{PLOT_NORTH}/photo", **kwargs)

    assert_problem(response, 503, "UNAVAILABLE")
    assert response.headers["retry-after"] == "5"
    assert s3.calls == []
    assert stored_row(db_url) == {"key": NORTH_KEY, "content_type": "image/jpeg"}
    assert "AWS_S3_BUCKET is not set" in caplog.text


@pytest.mark.parametrize("method", ["get", "post"])
def test_missing_database_returns_503(tmp_path: Path, s3, method):
    app.dependency_overrides[get_db] = database_from(tmp_path / "missing.db")
    kwargs = {"files": {"file": ("photo", JPEG, "image/jpeg")}} if method == "post" else {}

    response = getattr(TestClient(app), method)(f"/v1/plots/{PLOT_NORTH}/photo", **kwargs)

    assert_problem(response, 503, "UNAVAILABLE")
    assert s3.calls == []

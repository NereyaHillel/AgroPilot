"""Forecast cache and the fresh / retry / stale / 503 decision."""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from cache import Entry, cell_key
from config import Settings
from errors import UnavailableProblem
from provider import Day, OpenMeteo, ProviderError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Result:
    fetched_at: datetime
    stale: bool
    days: tuple[Day, ...]


def _local_today(now: datetime, offset_seconds: int) -> date:
    return (now + timedelta(seconds=offset_seconds)).date()


class ForecastService:
    def __init__(
        self,
        provider: OpenMeteo,
        settings: Settings,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._provider = provider
        self._settings = settings
        self._clock = clock
        self._sleep = sleep
        self._cache: dict[tuple[int, int], Entry] = {}
        self._locks: dict[tuple[int, int], threading.Lock] = {}
        self._mutex = threading.Lock()  # guards the two dicts, never held during a provider call

    @property
    def size(self) -> int:
        return len(self._cache)

    def get(self, lat: float, lon: float, days: int) -> Result:
        key = cell_key(lat, lon)
        entry = self._cache.get(key)
        if entry and self._is_fresh(entry, self._clock()):
            return Result(entry.fetched_at, False, entry.days[:days])
        # One provider call per cold cell, however many requests arrive together.
        with self._lock_for(key):
            entry = self._cache.get(key)
            if entry and self._is_fresh(entry, self._clock()):
                return Result(entry.fetched_at, False, entry.days[:days])
            fetched = self._fetch_with_retries(key)
            if fetched is not None:
                entry = Entry(self._clock(), fetched.utc_offset_seconds, fetched.days)
                self._store(key, entry)
                return Result(entry.fetched_at, False, entry.days[:days])
            return self._stale(key, entry, days)

    def _is_fresh(self, entry: Entry, now: datetime) -> bool:
        young = now - entry.fetched_at < timedelta(seconds=self._settings.fresh_seconds)
        # After local midnight yesterday's first day must not be served as today's.
        today = _local_today(now, entry.utc_offset_seconds) == entry.first_date
        return young and today

    def _fetch_with_retries(self, key: tuple[int, int]):
        lat, lon = key[0] / 10, key[1] / 10  # the cell's coordinates
        attempts = 1 + self._settings.provider_retries
        for attempt in range(1, attempts + 1):
            try:
                return self._provider.fetch(lat, lon)
            except ProviderError as error:
                logger.warning("provider attempt %d/%d failed: %s", attempt, attempts, error)
                if attempt < attempts:
                    self._sleep(self._settings.provider_retry_pause_seconds)
        return None

    def _stale(self, key: tuple[int, int], entry: Entry | None, days: int) -> Result:
        now = self._clock()
        if entry is not None and now - entry.fetched_at <= timedelta(
            seconds=self._settings.max_stale_seconds
        ):
            today = _local_today(now, entry.utc_offset_seconds)
            remaining = tuple(d for d in entry.days if d.date >= today)
            # Without today in it the forecast says nothing about now.
            if remaining and remaining[0].date == today:
                return Result(entry.fetched_at, True, remaining[:days])
        raise UnavailableProblem("Weather provider is unavailable and no recent forecast is cached")

    def _store(self, key: tuple[int, int], entry: Entry) -> None:
        # An entry past the stale limit can never be served, so it is dropped.
        limit = timedelta(seconds=self._settings.max_stale_seconds)
        with self._mutex:
            for old_key in [k for k, e in self._cache.items() if entry.fetched_at - e.fetched_at > limit]:
                del self._cache[old_key]
            self._cache[key] = entry

    def _lock_for(self, key: tuple[int, int]) -> threading.Lock:
        with self._mutex:
            return self._locks.setdefault(key, threading.Lock())

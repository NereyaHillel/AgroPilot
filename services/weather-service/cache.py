from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from provider import Day


def _tenths(value: float) -> int:
    # Decimal on the printed value, not round(): binary floats make round(x, 1) inconsistent
    # (0.05 is stored just below 0.05). Half rounds away from zero, so north/south and
    # east/west behave the same, and -0.0 becomes 0 because the key is an integer.
    return int(Decimal(repr(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) * 10)


def cell_key(lat: float, lon: float) -> tuple[int, int]:
    """The 0.1 degree grid cell of a point, as integer tenths of a degree."""
    return _tenths(lat), _tenths(lon)


@dataclass(frozen=True)
class Entry:
    fetched_at: datetime  # UTC time the provider was last successfully called
    utc_offset_seconds: int  # of the point, as reported by the provider
    days: tuple[Day, ...]

    @property
    def first_date(self) -> date:
        return self.days[0].date

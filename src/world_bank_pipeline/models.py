from dataclasses import dataclass
from typing import Any

class RecordValidationError(ValueError):
    """Raised when a World Bank record contains invalid data."""

@dataclass(frozen=True, slots=True)
class IndicatorRecord:
    """Normalized World Bank indicator record."""

    country_code: str
    country_name: str
    indicator_code: str
    indicator_name: str
    year: int
    value: int | float | None

    def __post_init__(self) -> None:
        if (
            len(self.country_code) != 3
            or not self.country_code.isalpha()
        ):
            raise RecordValidationError(
                f"Invalid country code: {self.country_code!r}"
            )

        if not 1800 <= self.year <= 2100:
            raise RecordValidationError(
                f"Invalid year: {self.year}"
            )

        if not self.indicator_code.strip():
            raise RecordValidationError(
                "Indicator code cannot be empty."
            )

        if isinstance(self.value, bool):
            raise RecordValidationError(
                "Indicator value cannot be a boolean."
            )

        if self.value is not None and not isinstance(
            self.value,
            (int, float),
        ):
            raise RecordValidationError(
                f"Invalid indicator value: {self.value!r}"
            )

    @classmethod
    def from_api(
        cls,
        record: dict[str, Any],
    ) -> "IndicatorRecord":
        """Create a validated record from a World Bank API response."""

        try:
            return cls(
                country_code=record["countryiso3code"],
                country_name=record["country"]["value"],
                indicator_code=record["indicator"]["id"],
                indicator_name=record["indicator"]["value"],
                year=int(record["date"]),
                value=record["value"],
            )

        except (KeyError, TypeError, ValueError) as exc:
            raise RecordValidationError(
                f"Malformed World Bank record: {record!r}"
            ) from exc

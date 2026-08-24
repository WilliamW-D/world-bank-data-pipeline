from typing import Any

from world_bank_pipeline.api_client import fetch_raw_indicator
from world_bank_pipeline.models import (
    IndicatorRecord,
    RecordValidationError,
)

def normalize_records(
    raw_records: list[dict[str, Any]],
) -> list[IndicatorRecord]:
    """Validate and normalize raw World Bank records."""

    normalized: list[IndicatorRecord] = []

    for index, raw_record in enumerate(raw_records):
        try:
            record = IndicatorRecord.from_api(raw_record)

        except RecordValidationError as exc:
            raise RecordValidationError(
                f"Record {index} failed validation: {exc}"
            ) from exc

        normalized.append(record)

    return normalized

def fetch_indicator(
    country: str,
    indicator: str,
    start_year: int,
    end_year: int,
) -> list[IndicatorRecord]:
    """Retrieve and normalize World Bank indicator records."""

    raw_records = fetch_raw_indicator(
        country=country,
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
    )

    return normalize_records(raw_records)

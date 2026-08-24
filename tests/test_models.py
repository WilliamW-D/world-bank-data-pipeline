import pytest

from world_bank_pipeline.models import (
    IndicatorRecord,
    RecordValidationError,
)

def make_valid_record() -> dict:
    return {
        "countryiso3code": "USA",
        "country": {
            "value": "United States",
        },
        "indicator": {
            "id": "NY.GDP.MKTP.CD",
            "value": "GDP (current US$)",
        },
        "date": "2024",
        "value": 29184700000000,
    }

def test_record_created_from_valid_api_data() -> None:
    record = IndicatorRecord.from_api(
        make_valid_record()
    )
    
    assert record.country_code == "USA"
    assert record.country_name == "United States"
    assert record.indicator_code == "NY.GDP.MKTP.CD"
    assert record.year == 2024
    assert record.value == 29184700000000

def test_missing_indicator_value_is_allowed() -> None:
    raw_record = make_valid_record()
    raw_record["value"] = None
    
    record = IndicatorRecord.from_api(raw_record)
    
    assert record.value is None

def test_invalid_country_code_is_rejected() -> None:
    raw_record = make_valid_record()
    raw_record["countryiso3code"] = "US"
    
    with pytest.raises(RecordValidationError):
        IndicatorRecord.from_api(raw_record)

def test_missing_required_field_is_rejected() -> None:
    raw_record = make_valid_record()
    del raw_record["indicator"]
    
    with pytest.raises(RecordValidationError):
        IndicatorRecord.from_api(raw_record)

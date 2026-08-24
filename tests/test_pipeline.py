import pytest

from world_bank_pipeline.models import RecordValidationError
from world_bank_pipeline.pipeline import normalize_records

def test_normalize_records() -> None:
    raw_records = [
        {
            "countryiso3code": "USA",
            "country": {
                "value": "United States",
            },
            "indicator": {
                "id": "SP.POP.TOTL",
                "value": "Population, total",
            },
            "date": "2023",
            "value": 334914895,
        }
    ]
    
    records = normalize_records(raw_records)
    
    assert len(records) == 1
    assert records[0].country_code == "USA"
    assert records[0].year == 2023
    assert records[0].value == 334914895

def test_invalid_record_reports_position() -> None:
    raw_records = [
        {
            "countryiso3code": "USA",
            "country": {
                "value": "United States",
            },
            "indicator": {
                "id": "SP.POP.TOTL",
                "value": "Population, total",
            },
            "date": "2023",
            "value": 334914895,
        },
        {
            "countryiso3code": "XX",
            "country": {
                "value": "Invalid",
            },
            "indicator": {
                "id": "SP.POP.TOTL",
                "value": "Population, total",
            },
            "date": "2023",
            "value": 1,
        },
    ]
    
    with pytest.raises(
        RecordValidationError,
        match="Record 1",
    ):
        normalize_records(raw_records)

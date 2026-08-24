from unittest.mock import Mock

import pytest
import requests

from world_bank_pipeline.api_client import (
    DEFAULT_RETRIES,
    WorldBankAPIError,
    create_session,
    fetch_raw_indicator,
)

def make_api_payload() -> list:
    return [
        {
            "page": 1,
            "pages": 1,
            "per_page": 100,
            "total": 1,
        },
        [
            {
                "indicator": {
                    "id": "SP.POP.TOTL",
                    "value": "Population, total",
                },
                "country": {
                    "id": "US",
                    "value": "United States",
                },
                "countryiso3code": "USA",
                "date": "2024",
                "value": 340000000,
            }
        ],
    ]

def test_successful_api_response() -> None:
    mock_response = Mock()
    
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = make_api_payload()
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    
    records = fetch_raw_indicator(
        country="USA",
        indicator="SP.POP.TOTL",
        start_year=2024,
        end_year=2024,
        session=mock_session,
    )
    
    assert len(records) == 1
    assert records[0]["countryiso3code"] == "USA"
    
    mock_session.get.assert_called_once()

def test_http_failure_raises_api_error() -> None:
    mock_response = Mock()
    
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError(
            "503 Service Unavailable"
        )
    )
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    
    with pytest.raises(
        WorldBankAPIError,
        match="request failed",
    ):
        fetch_raw_indicator(
            country="USA",
            indicator="SP.POP.TOTL",
            start_year=2024,
            end_year=2024,
            session=mock_session,
        )

def test_invalid_json_raises_api_error() -> None:
    mock_response = Mock()
    
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError(
        "Invalid JSON"
    )
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    
    with pytest.raises(
        WorldBankAPIError,
        match="invalid JSON",
    ):
        fetch_raw_indicator(
            country="USA",
            indicator="SP.POP.TOTL",
            start_year=2024,
            end_year=2024,
            session=mock_session,
        )

def test_empty_api_results_return_empty_list() -> None:
    mock_response = Mock()
    
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "page": 1,
            "pages": 0,
            "total": 0,
        },
        None,
    ]
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    
    records = fetch_raw_indicator(
        country="USA",
        indicator="SP.POP.TOTL",
        start_year=2024,
        end_year=2024,
        session=mock_session,
    )
    
    assert records == []

def test_invalid_year_range_is_rejected() -> None:
    mock_session = Mock()
    
    with pytest.raises(
        ValueError,
        match="start_year",
    ):
        fetch_raw_indicator(
            country="USA",
            indicator="SP.POP.TOTL",
            start_year=2025,
            end_year=2020,
            session=mock_session,
        )
        
    mock_session.get.assert_not_called()

def test_session_has_retry_policy() -> None:
    session = create_session()
    
    try:
        adapter = session.get_adapter(
            "https://"
        )
        
        retries = adapter.max_retries
        
        assert retries.total == DEFAULT_RETRIES
        
        assert 429 in retries.status_forcelist
        assert 500 in retries.status_forcelist
        assert 503 in retries.status_forcelist
        
        assert "GET" in retries.allowed_methods
        
    finally:
        session.close()

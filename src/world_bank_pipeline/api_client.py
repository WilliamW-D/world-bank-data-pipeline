from typing import Any

import requests

BASE_URL = "https://api.worldbank.org/v2"

class WorldBankAPIError(Exception):
    """Raised when the World Bank API request fails."""

def fetch_indicator(
    country: str,
    indicator: str,
    start_year: int,
    end_year: int,
) -> list[dict[str, Any]]:
    """
    Fetch indicator data from the World Bank API.
    
    Args:
        country: World Bank country code, such as "USA".
        indicator: Indicator code, such as "NY.GDP.MKTP.CD".
        start_year: First year to retrieve.
        end_year: Last year to retrieve.
        
    Returns:
        A normalized list of indicator records.
    """
    
    url = f"{BASE_URL}/country/{country}/indicator/{indicator}"
    
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 100,
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        
    except requests.RequestException as exc:
        raise WorldBankAPIError(
            f"World Bank API request failed: {exc}"
        ) from exc
        
    payload = response.json()
    
    if not isinstance(payload, list) or len(payload) < 2:
        raise WorldBankAPIError(
            "World Bank API returned an unexpected response."
        )
        
    records = payload[1]
    
    if records is None:
        return []
        
    return [
        {
            "country_code": record["countryiso3code"],
            "country_name": record["country"]["value"],
            "indicator_code": record["indicator"]["id"],
            "indicator_name": record["indicator"]["value"],
            "year": int(record["date"]),
            "value": record["value"],
        }
        for record in records
    ]

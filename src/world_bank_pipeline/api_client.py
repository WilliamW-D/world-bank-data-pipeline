from typing import Any

import requests

BASE_URL = "https://api.worldbank.org/v2"

class WorldBankAPIError(Exception):
    """Raised when communication with the World Bank API fails."""

def fetch_raw_indicator(
    country: str,
    indicator: str,
    start_year: int,
    end_year: int,
) -> list[dict[str, Any]]:
    """Retrieve raw indicator records from the World Bank API."""

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    url = (
        f"{BASE_URL}/country/"
        f"{country}/indicator/{indicator}"
    )

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

    try:
        payload = response.json()

    except ValueError as exc:
        raise WorldBankAPIError(
            "World Bank API returned invalid JSON."
        ) from exc

    if not isinstance(payload, list) or len(payload) < 2:
        raise WorldBankAPIError(
            "World Bank API returned an unexpected response."
        )

    records = payload[1]

    if records is None:
        return []

    if not isinstance(records, list):
        raise WorldBankAPIError(
            "World Bank API records were not returned as a list."
        )

    return records

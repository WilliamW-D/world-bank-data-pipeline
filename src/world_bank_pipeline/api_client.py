import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.worldbank.org/v2"

DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5

logger = logging.getLogger(__name__)

class WorldBankAPIError(Exception):
    """Raised when communication with the World Bank API fails."""

def create_session() -> requests.Session:
    """Create an HTTP session configured with retry behavior."""
    
    retry_strategy = Retry(
        total=DEFAULT_RETRIES,
        connect=DEFAULT_RETRIES,
        read=DEFAULT_RETRIES,
        status=DEFAULT_RETRIES,
        backoff_factor=DEFAULT_BACKOFF_FACTOR,
        status_forcelist=[
            429,
            500,
            502,
            503,
            504,
        ],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
    )
    
    session = requests.Session()
    
    session.mount(
        "https://",
        adapter,
    )
    
    session.mount(
        "http://",
        adapter,
    )
    
    session.headers.update(
        {
            "User-Agent": (
                "world-bank-data-pipeline/0.1"
            )
        }
    )
    
    return session

def fetch_raw_indicator(
    country: str,
    indicator: str,
    start_year: int,
    end_year: int,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Retrieve raw indicator records from the World Bank API."""
    
    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )
        
    country = country.upper().strip()
    indicator = indicator.strip()
    
    url = (
        f"{BASE_URL}/country/"
        f"{country}/indicator/{indicator}"
    )
    
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 100,
    }
    
    logger.info(
        "Requesting indicator=%s country=%s years=%s-%s",
        indicator,
        country,
        start_year,
        end_year,
    )
    
    owns_session = session is None
    
    if session is None:
        session = create_session()
        
    try:
        response = session.get(
            url,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        
        response.raise_for_status()
        
    except requests.RequestException as exc:
        logger.error(
            "World Bank API request failed: %s",
            exc,
        )
        
        raise WorldBankAPIError(
            f"World Bank API request failed: {exc}"
        ) from exc
        
    finally:
        if owns_session:
            session.close()

    try:
        payload = response.json()

    except ValueError as exc:
        logger.error(
            "World Bank API returned invalid JSON."
        )
        
        raise WorldBankAPIError(
            "World Bank API returned invalid JSON."
        ) from exc

    if not isinstance(payload, list) or len(payload) < 2:
        raise WorldBankAPIError(
            "World Bank API returned an unexpected response."
        )

    records = payload[1]

    if records is None:
        logger.info(
            "World Bank returned no records."
        )
        
        return []

    if not isinstance(records, list):
        raise WorldBankAPIError(
            "World Bank API records were not returned as a list."
        )
        
    logger.info(
        "World Bank returned %d raw records.",
        len(records),
    )

    return records

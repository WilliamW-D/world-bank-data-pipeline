# World Bank Data Pipeline

[![Tests](https://github.com/WilliamW-D/world-bank-data-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/WilliamW-D/world-bank-data-pipeline/actions/workflows/tests.yml)

A production-style Python ETL pipeline that retrieves economic and demographic indicators from the World Bank API, validates the data, and stores it in SQLite for analysis.

The project demonstrates API integration, data modeling, validation, SQL persistence, automated testing, retry strategies, and continuous integration.

## Why I Built This

Pulling data from an API is straightforward.

Building a data pipeline that can be rerun safely, handle unreliable external services, validate incoming records, and prevent duplicate data requires a professional engineering approach.

This project was built to demonstrate those production-oriented concerns in a small, understandable Python application.

## Architecture

```text
               World Bank API
                     |
                     v
        +-------------------------+
        |       API Client        |
        |     HTTP + Retries      |
        +-------------------------+
                     |
              Raw API Records
                     |
                     v
        +-------------------------+
        |     Data Pipeline       |
        |     Normalization       |
        +-------------------------+
                     |
                     v
        +-------------------------+
        |    IndicatorRecord      |
        |      Validation         |
        +-------------------------+
                     |
                     v
        +-------------------------+
        |         SQLite          |
        |    Upsert + Unique      |
        |      Constraints        |
        +-------------------------+
```

## Engineering Features

- REST API integration with the World Bank API
- Typed Python data models
- Validation of incoming API records
- Separation between retrieval, transformation, and persistence
- SQLite relational database
- Parameterized SQL queries
- Database uniqueness constraints
- Upsert behavior for revised records
- HTTP retry and backoff handling
- Structured application logging
- Configurable command-line interface
- Automated unit tests with pytest
- Mocked API tests that do not require internet access
- Temporary isolated databases during database tests
- GitHub Actions continuous integration
- Automated testing across multiple Python versions

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| API | World Bank REST API |
| HTTP | Requests |
| Database | SQLite |
| Testing | pytest |
| Mocking | unittest.mock |
| CI | GitHub Actions |
| Packaging | pyproject.toml / setuptools |
| Version Control | Git / GitHub |

## Project Structure

```text
world-bank-data-pipeline/
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── data/
│   └── .gitkeep
│
├── src/
│   └── world_bank_pipeline/
│       ├── __init__.py
│       ├── api_client.py
│       ├── cli.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       └── pipeline.py
│
├── tests/
│   ├── test_api_client.py
│   ├── test_database.py
│   ├── test_models.py
│   └── test_pipeline.py
│
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/WilliamW-D/world-bank-data-pipeline.git
cd world-bank-data-pipeline
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

Retrieve U.S. population data from 2020 through 2024:

```bash
python -m world_bank_pipeline.cli --country USA --indicator SP.POP.TOTL --start-year 2020 --end-year 2024
```

Example output:

```text
2026-08-23 23:00:00 | INFO | world_bank_pipeline.api_client | Requesting indicator=SP.POP.TOTL country=USA years=2020-2024
2026-08-23 23:00:01 | INFO | world_bank_pipeline.api_client | World Bank returned 5 raw records.
2026-08-23 23:00:01 | INFO | world_bank_pipeline.database | Processed 5 database records.

Retrieved 5 records from the World Bank API.
Stored 5 records in data/world_bank.db.
```

Retrieve GDP data for Canada:

```bash
python -m world_bank_pipeline.cli --country CAN --indicator NY.GDP.MKTP.CD --start-year 2015 --end-year 2024
```

Specify another SQLite database:

```bash
python -m world_bank_pipeline.cli --country USA --database data/custom.db
```

Enable debug logging:

```bash
python -m world_bank_pipeline.cli --log-level DEBUG
```

## Database Design

Indicator data is stored in the `indicator_records` table.

Important fields include:

```text
country_code
country_name
indicator_code
indicator_name
year
value
created_at
updated_at
```

The combination of:

```text
country_code + indicator_code + year
```

is unique.

This makes the pipeline idempotent for a given indicator and year. Running the same extraction repeatedly does not create duplicate records.

If the World Bank later revises a value, the pipeline updates the existing record using SQLite upsert behavior.

## Error Handling

External API calls can fail temporarily due to network problems, rate limiting, or server errors.

The HTTP client automatically retries transient failures including:

```text
429 Too Many Requests
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
```

The pipeline also detects:
- Invalid HTTP responses
- Invalid JSON
- Unexpected API response structures
- Invalid year ranges
- Malformed indicator records
- Invalid country codes
- Invalid indicator values

Failures are surfaced through application-specific exceptions and structured logging.

## Testing

Run the complete test suite with:

```bash
pytest -q
```

The project tests:
- API response handling
- Invalid HTTP responses
- Invalid JSON
- Empty API results
- Input validation
- Record normalization
- Data-model validation
- Database creation
- Database inserts
- Duplicate prevention
- Updating existing records
- Multiple-year storage
- HTTP retry configuration

API tests use mocked HTTP sessions, so the automated test suite does not depend on the World Bank API being online.

Database tests use temporary SQLite databases to keep tests isolated from local application data.

## Continuous Integration

GitHub Actions runs the automated test suite whenever code is pushed to `main` or included in a pull request targeting `main`.

Tests run in clean Linux environments across multiple supported Python versions.

This verifies that the project works outside the developer's local environment.

## Design Decisions

### Why SQLite?

SQLite provides relational constraints, SQL queries, transactions, and upsert behavior without requiring external infrastructure. It keeps the project easy to run while still demonstrating database design and persistence.

### Why separate the API client from the pipeline?

The API client is responsible only for communication with the external service.

Transformation and validation happen separately.

This separation makes the code easier to test, maintain, and replace if the external data source changes.

### Why use mocked API tests?

Automated tests should be deterministic. Depending on a live external API would make the test suite vulnerable to network outages, rate limits, and changes outside the application.

Mocking allows API behavior and failure conditions to be tested consistently.

### Why use upserts?

Economic datasets can be revised after publication. Ignoring existing records would preserve outdated information, while inserting everything again would create duplicates.

Upserts allow existing observations to be updated safely.

## Possible Future Improvements

Potential extensions include:
- PostgreSQL support
- Multiple-country batch ingestion
- Multiple-indicator ingestion
- CSV and JSON export
- Scheduled pipeline execution
- Incremental synchronization
- Data-quality reporting
- Docker containerization

import argparse
from pathlib import Path

from world_bank_pipeline.api_client import WorldBankAPIError
from world_bank_pipeline.database import (
    DEFAULT_DATABASE_PATH,
    connect_database,
    initialize_database,
)
from world_bank_pipeline.models import RecordValidationError
from world_bank_pipeline.pipeline import (
    fetch_indicator,
    store_indicator_records,
)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve World Bank indicator data."
    )
    
    parser.add_argument(
        "--country",
        default="USA",
        help="World Bank country code. Default: USA",
    )
    
    parser.add_argument(
        "--indicator",
        default="NY.GDP.MKTP.CD",
        help="World Bank indicator code.",
    )
    
    parser.add_argument(
        "--start-year",
        type=int,
        default=2020,
        help="First year to retrieve.",
    )
    
    parser.add_argument(
        "--end-year",
        type=int,
        default=2024,
        help="Last year to retrieve.",
    )
    
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help=(
            "SQLite database path. "
            f"Default: {DEFAULT_DATABASE_PATH}"
        ),
    )
    
    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    
    try:
        records = fetch_indicator(
            country=args.country,
            indicator=args.indicator,
            start_year=args.start_year,
            end_year=args.end_year,
        )
        
    except (
        WorldBankAPIError,
        RecordValidationError,
        ValueError,
    ) as exc:
        print(f"Error: {exc}")
        return
        
    if not records:
        print("No records found.")
        return
        
    with connect_database(args.database) as connection:
        initialize_database(connection)
        
        records_processed = store_indicator_records(
            connection=connection,
            records=records,
        )
        
    print(
        f"Retrieved {len(records)} records "
        f"from the World Bank API."
    )
    
    print(
        f"Stored {records_processed} records "
        f"in {args.database}."
    )

if __name__ == "__main__":
    main()

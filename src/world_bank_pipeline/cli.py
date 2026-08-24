import argparse

from world_bank_pipeline.api_client import WorldBankAPIError
from world_bank_pipeline.models import RecordValidationError
from world_bank_pipeline.pipeline import fetch_indicator

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
        
    for record in records:
        value = (
            record.value
            if record.value is not None
            else "N/A"
        )
        
        print(
            f"{record.country_code} | "
            f"{record.year} | "
            f"{record.indicator_code} | "
            f"{value}"
        )

if __name__ == "__main__":
    main()

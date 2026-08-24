from pathlib import Path

from world_bank_pipeline.database import (
    connect_database,
    count_records,
    fetch_records,
    initialize_database,
    save_records,
)
from world_bank_pipeline.models import IndicatorRecord


def make_record(
    *,
    year: int = 2024,
    value: float = 100.0,
) -> IndicatorRecord:
    return IndicatorRecord(
        country_code="USA",
        country_name="United States",
        indicator_code="TEST.INDICATOR",
        indicator_name="Test Indicator",
        year=year,
        value=value,
    )


def test_initialize_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.db"
    
    with connect_database(database_path) as connection:
        initialize_database(connection)
        
        table = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'indicator_records'
            """
        ).fetchone()
        
        assert table is not None


def test_save_record(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.db"
    
    with connect_database(database_path) as connection:
        initialize_database(connection)
        
        save_records(
            connection,
            [make_record()],
        )
        
        assert count_records(connection) == 1


def test_duplicate_record_is_not_created(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.db"
    
    record = make_record()
    
    with connect_database(database_path) as connection:
        initialize_database(connection)
        
        save_records(
            connection,
            [record],
        )
        
        save_records(
            connection,
            [record],
        )
        
        assert count_records(connection) == 1


def test_existing_record_is_updated(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.db"
    
    original = make_record(
        value=100.0,
    )
    
    revised = make_record(
        value=200.0,
    )
    
    with connect_database(database_path) as connection:
        initialize_database(connection)
        
        save_records(
            connection,
            [original],
        )
        
        save_records(
            connection,
            [revised],
        )
        
        rows = fetch_records(
            connection,
            country_code="USA",
            indicator_code="TEST.INDICATOR",
        )
        
        assert len(rows) == 1
        assert rows[0]["value"] == 200.0


def test_multiple_years_are_stored(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.db"
    
    records = [
        make_record(
            year=2022,
            value=100.0,
        ),
        make_record(
            year=2023,
            value=200.0,
        ),
        make_record(
            year=2024,
            value=300.0,
        ),
    ]
    
    with connect_database(database_path) as connection:
        initialize_database(connection)
        
        save_records(
            connection,
            records,
        )
        
        assert count_records(connection) == 3


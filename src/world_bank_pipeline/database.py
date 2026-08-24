import sqlite3
from collections.abc import Iterable
from pathlib import Path

from world_bank_pipeline.models import IndicatorRecord

DEFAULT_DATABASE_PATH = Path("data/world_bank.db")


def connect_database(
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> sqlite3.Connection:
    """Create a SQLite connection and ensure its directory exists."""

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(
    connection: sqlite3.Connection,
) -> None:
    """Create database tables if they do not already exist."""

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS indicator_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            country_code TEXT NOT NULL,
            country_name TEXT NOT NULL,
            
            indicator_code TEXT NOT NULL,
            indicator_name TEXT NOT NULL,
            
            year INTEGER NOT NULL,
            value REAL,
            
            created_at TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
                
            updated_at TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
                
            UNIQUE (
                country_code,
                indicator_code,
                year
            )
        )
        """
    )
    
    connection.commit()


def save_records(
    connection: sqlite3.Connection,
    records: Iterable[IndicatorRecord],
) -> int:
    """
    Insert or update indicator records.
    
    Returns the number of records processed.
    """

    records_processed = 0

    sql = """
        INSERT INTO indicator_records (
            country_code,
            country_name,
            indicator_code,
            indicator_name,
            year,
            value
        )
        VALUES (?, ?, ?, ?, ?, ?)
        
        ON CONFLICT (
            country_code,
            indicator_code,
            year
        )
        DO UPDATE SET
            country_name = excluded.country_name,
            indicator_name = excluded.indicator_name,
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
    """

    for record in records:
        connection.execute(
            sql,
            (
                record.country_code,
                record.country_name,
                record.indicator_code,
                record.indicator_name,
                record.year,
                record.value,
            ),
        )
        
        records_processed += 1

    connection.commit()
    
    return records_processed


def count_records(
    connection: sqlite3.Connection,
) -> int:
    """Return the number of indicator records in the database."""

    row = connection.execute(
        """
        SELECT COUNT(*) AS record_count
        FROM indicator_records
        """
    ).fetchone()

    return int(row["record_count"])


def fetch_records(
    connection: sqlite3.Connection,
    country_code: str | None = None,
    indicator_code: str | None = None,
) -> list[sqlite3.Row]:
    """Retrieve stored records with optional filters."""

    sql = """
        SELECT
            country_code,
            country_name,
            indicator_code,
            indicator_name,
            year,
            value,
            created_at,
            updated_at
        FROM indicator_records
        WHERE 1 = 1
    """

    parameters: list[str] = []

    if country_code:
        sql += " AND country_code = ?"
        parameters.append(country_code)

    if indicator_code:
        sql += " AND indicator_code = ?"
        parameters.append(indicator_code)

    sql += """
        ORDER BY
            country_code,
            indicator_code,
            year DESC
    """

    cursor = connection.execute(
        sql,
        parameters,
    )

    return cursor.fetchall()

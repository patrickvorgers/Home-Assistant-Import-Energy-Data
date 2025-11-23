"""
CSV Import Script for Sensor Data

This script imports CSV files into a unified `import_data` table in either SQLite or MariaDB.
Each CSV is expected to contain two columns: timestamp and value.

- The sensor ID and resolution are extracted from the CSV filename.
  Example:
    "elec_solar_high_resolution.csv" → id: sensor_id_elec_solar, resolution: HIGH
    "gas_low_resolution.csv"         → id: sensor_id_gas,        resolution: LOW

- The table `import_data` uses a composite primary key (id, resolution, timestamp).

- The script supports:
  ✓ Wildcard CSV input (e.g., data/*.csv)
  ✓ Efficient batch inserts via executemany()
  ✓ Optional suppression of table recreation
  ✓ Type-safe DB selection
  ✓ Duplicate key handling for both SQLite and MariaDB

Typical usage:
  python script.py --db-type sqlite --sqlite-db db.sqlite --csv-file "data/*.csv"
  python script.py --db-type mariadb --user root --database mydb --csv-file "data/*.csv"
  python script.py --db-type mariadb --user root --database mydb --cleanup-backup
"""
import argparse
import csv
import glob
import os
from enum import Enum, auto


class DatabaseType(Enum):
    """Supported database backends."""

    SQLITE = auto()
    MARIADB = auto()


def log(message: str, verbose: bool = True):
    """Prints a message if verbose mode is enabled."""
    if verbose:
        print(message)


def parse_db_type(db_type_str: str) -> DatabaseType:
    """
    Converts a string argument into a DatabaseType Enum.
    """
    db_type_map = {
        "sqlite": DatabaseType.SQLITE,
        "mariadb": DatabaseType.MARIADB,
    }
    try:
        return db_type_map[db_type_str.lower()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid database type: {db_type_str}")


def get_connection(db_type: DatabaseType, args):
    """
    Establishes a database connection and returns the connection and placeholder symbol.
    """
    if db_type == DatabaseType.SQLITE:
        import sqlite3

        if not args.sqlite_db:
            raise ValueError("--sqlite-db is required for SQLite")
        conn = sqlite3.connect(args.sqlite_db)
        # SQLite uses '?' for placeholders
        placeholder = "?"
    elif db_type == DatabaseType.MARIADB:
        import mysql.connector

        if not args.user or not args.database:
            raise ValueError("--user and --database are required for MariaDB")
        # Use an empty password if none is provided
        password = args.password if args.password is not None else ""
        conn = mysql.connector.connect(
            host=args.host, user=args.user, password=password, database=args.database
        )
        # MariaDB/MySQL uses '%s' for placeholders
        placeholder = "%s"
    else:
        raise ValueError("Unsupported database type.")

    return conn, placeholder


def create_table(cursor, recreate: bool = True, verbose: bool = False):
    """
    Creates the `IMPORT_DATA` table with the appropriate schema.
    If `recreate` is True, drops the table first.
    """
    if recreate:
        log("🔄 Dropping existing IMPORT_DATA table", verbose)
        cursor.execute("DROP TABLE IF EXISTS IMPORT_DATA")

        log("🛠️ Creating IMPORT_DATA table")
    else:
        log("🧱 Keeping existing IMPORT_DATA table (created if missing)", verbose)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS IMPORT_DATA (
            id VARCHAR(50) NOT NULL,
            resolution VARCHAR(4) NOT NULL,
            timestamp DOUBLE NOT NULL,
            value DOUBLE NOT NULL,
            PRIMARY KEY (id, resolution, timestamp),
            CHECK (resolution IN ('HIGH','LOW'))
        )
    """
    )


def compute_id_and_resolution(csv_file: str) -> tuple[str, str]:
    """
    Extract the id and resolution from the CSV file name.

    The file name must end with either "high_resolution.csv" or "low_resolution.csv".
    The id is the part of the file name preceding the suffix, with any trailing underscore removed.
    The id is then prepended with 'sensor_id_'.

    Examples:
        "deviceX_high_resolution.csv" --> id: "sensor_id_deviceX", resolution: "HIGH"
        "abc123_low_resolution.csv"   --> id: "sensor_id_abc123", resolution: "LOW"

    Fallback:
        If neither suffix is present, the resolution defaults to HIGH.
        The id is the file name without extension (any trailing underscore removed),
        and a message is printed to inform the user that HIGH was assumed.
    """
    basename = os.path.basename(csv_file)
    lower_basename = basename.lower()

    if lower_basename.endswith("high_resolution.csv"):
        suffix = "high_resolution.csv"
        resolution = "HIGH"
        id_part = basename[: -len(suffix)]
    elif lower_basename.endswith("low_resolution.csv"):
        suffix = "low_resolution.csv"
        resolution = "LOW"
        id_part = basename[: -len(suffix)]
    else:
        # No explicit resolution: assume HIGH and inform the user.
        log(
            f"ℹ️ No 'high_resolution' or 'low_resolution' suffix found in '{basename}'. "
            f"Assuming HIGH resolution."
        )
        name_without_ext, _ = os.path.splitext(basename)
        id_part = name_without_ext
        resolution = "HIGH"

    if id_part.endswith("_"):
        id_part = id_part[:-1]

    return id_part, resolution


def expand_file_patterns(patterns: list[str]) -> list[str]:
    """
    Expand each file pattern (which may include wildcards) into a list of files.
    """
    files = []
    for pattern in patterns:
        matched = glob.glob(pattern)
        if not matched:
            log(f"⚠️ Warning: No files found matching pattern '{pattern}'")
        else:
            files.extend(matched)
    return files


def import_csv_data(
    cursor,
    csv_file: str,
    placeholder: str,
    id_val: str,
    resolution: str,
    db_type: DatabaseType,
) -> tuple[int, int]:
    """
    Efficiently imports data from a CSV into the IMPORT_DATA table with upsert support.
    Each CSV file is expected to have two columns: timestamp and value.
    The computed id_val and resolution values are used for every row.
    """
    base_query = (
        f"INSERT INTO IMPORT_DATA (id, resolution, timestamp, value) "
        f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}) "
    )

    if db_type == DatabaseType.SQLITE:
        conflict_clause = "ON CONFLICT(id, resolution, timestamp) DO UPDATE SET value = excluded.value"
    elif db_type == DatabaseType.MARIADB:
        conflict_clause = "ON DUPLICATE KEY UPDATE value = VALUES(value)"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    insert_query = base_query + conflict_clause

    rows = []
    total_rows = 0
    with open(csv_file, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            total_rows += 1
            if len(row) != 2:
                continue
            try:
                ts = float(row[0])
                val = float(row[1])
                rows.append((id_val, resolution, ts, val))
            except ValueError:
                continue

    if rows:
        cursor.executemany(insert_query, rows)

    processed_count = len(rows)
    skipped_count = total_rows - processed_count

    return processed_count, skipped_count


def main():
    """
    Entry point for the CSV import script.
    Handles argument parsing, database setup, and CSV processing.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Import one or more CSV files (timestamp and value) into the IMPORT_DATA table. "
            "The id and resolution are derived from each CSV file name. "
            "Filenames may end with 'high_resolution.csv' or 'low_resolution.csv'; "
            "if no such suffix is present, HIGH resolution is assumed. "
            "By default, the table is dropped and recreated; use --suppress-recreate to keep the existing table."
        )
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging output."
    )
    parser.add_argument(
        "--db-type",
        type=parse_db_type,
        required=True,
        help="Type of database to use: sqlite or mariadb",
    )
    parser.add_argument(
        "--csv-file",
        nargs="+",
        help="Path(s) or wildcard pattern(s) to one or more CSV files. Required unless --cleanup-backup is used.",
    )

    # SQLite-specific parameters
    parser.add_argument(
        "--sqlite-db", help="SQLite database file path (required for sqlite)"
    )

    # MariaDB-specific parameters
    parser.add_argument(
        "--host", default="localhost", help="MariaDB host (default: localhost)"
    )
    parser.add_argument("--user", help="MariaDB username (required for mariadb)")
    parser.add_argument(
        "--password", help="MariaDB password (default: empty if not set)"
    )
    parser.add_argument(
        "--database", help="MariaDB database name (required for mariadb)"
    )

    # Control table recreation
    parser.add_argument(
        "--suppress-recreate",
        action="store_true",
        help="If set, the existing IMPORT_DATA table will not be dropped/recreated (default drops the table).",
    )

    # Exclusive option for cleaning up backup tables.
    parser.add_argument(
        "--cleanup-backup",
        action="store_true",
        help="Cleanup backup data by dropping backup tables and exit.",
    )

    args = parser.parse_args()
    if not args.cleanup_backup and not args.csv_file:
        parser.error("--csv-file is required unless --cleanup-backup is used")
    db_type = args.db_type

    conn = None
    cursor = None

    try:
        # Establish database connection
        conn, placeholder = get_connection(db_type, args)
        cursor = conn.cursor()

        # Cleanup backup tables and exit if --cleanup-backup is specified.
        if args.cleanup_backup:
            log("🧹 Cleaning up backup tables")
            cursor.execute("DROP TABLE IF EXISTS BACKUP_STATISTICS")
            cursor.execute("DROP TABLE IF EXISTS BACKUP_STATISTICS_SHORT_TERM")
            conn.commit()
            log("✅ Backup cleanup completed")
            return

        log("🚀 Starting CSV import process")
        # Expand wildcards in CSV file arguments (only executed if not cleaning up backup)
        csv_files = expand_file_patterns(args.csv_file)
        if not csv_files:
            raise ValueError("No CSV files to process.")

        # Recreate table unless suppression is requested
        create_table(
            cursor, recreate=(not args.suppress_recreate), verbose=args.verbose
        )
        conn.commit()

        # Process each CSV file.
        for csv_file in csv_files:
            id_val, resolution = compute_id_and_resolution(csv_file)
            log(
                f"📥 Importing '{csv_file}' with id: '{id_val}' and resolution: '{resolution}'"
            )
            processed_count, skipped_count = import_csv_data(
                cursor, csv_file, placeholder, id_val, resolution, db_type
            )
            log(
                f"🔢 Processed {processed_count} records from '{csv_file}'", args.verbose
            )
            if skipped_count > 0:
                log(
                    f"🚫 Skipped {skipped_count} malformed records from '{csv_file}'",
                    args.verbose,
                )
            conn.commit()

        log("✅ CSV import completed")
    except Exception as e:
        log("❌ An error occurred: " + str(e))
    finally:
        # Make sure we always close the connection
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":  # pragma: no cover
    main()

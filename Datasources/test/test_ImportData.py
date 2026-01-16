# test_ImportData.py
# Unit tests for ImportData.py
# Usage for coverage check: python -m pytest test --cov=ImportData --cov-report=term-missing
# test_ImportData.py

import argparse
import contextlib
import sqlite3
import sys
import types
from enum import Enum
from pathlib import Path

import pytest
from ImportData import (
    DatabaseType,
    compute_id_and_resolution,
    create_table,
    expand_file_patterns,
    get_connection,
    import_csv_data,
    log,
    main,
    parse_db_type,
)

# ---------- helpers ----------


@contextlib.contextmanager
def sqlite_import_table(recreate: bool = True):
    """Context manager that creates an in-memory IMPORT_DATA table and closes the DB."""
    conn = sqlite3.connect(":memory:")
    try:
        cursor = conn.cursor()
        create_table(cursor, recreate=recreate, verbose=False)
        conn.commit()
        yield conn, cursor
    finally:
        conn.close()


class DummyCursor:
    """Very small stub cursor for testing SQL generation without a real DB."""

    def __init__(self):
        self.executed_queries: list[str] = []
        self.params: list[tuple] = []

    def executemany(self, query, seq_of_params):
        self.executed_queries.append(query)
        self.params.extend(seq_of_params)


def _install_fake_mysql(monkeypatch, fake_connect):
    """Install a fake mysql.connector module that uses `fake_connect`."""
    mysql_mod = types.ModuleType("mysql")
    connector_mod = types.ModuleType("mysql.connector")
    connector_mod.connect = fake_connect
    mysql_mod.connector = connector_mod

    monkeypatch.setitem(sys.modules, "mysql", mysql_mod)
    monkeypatch.setitem(sys.modules, "mysql.connector", connector_mod)


# ---------- parse_db_type ----------


def test_parse_db_type_sqlite():
    assert parse_db_type("sqlite") is DatabaseType.SQLITE
    assert parse_db_type("SQLITE") is DatabaseType.SQLITE


def test_parse_db_type_mariadb():
    assert parse_db_type("mariadb") is DatabaseType.MARIADB
    assert parse_db_type("MariaDB") is DatabaseType.MARIADB


def test_parse_db_type_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_db_type("postgres")


# ---------- compute_id_and_resolution ----------


def test_compute_id_and_resolution_high_suffix():
    id_part, resolution = compute_id_and_resolution(
        "/some/path/deviceX_high_resolution.csv"
    )
    assert id_part == "deviceX"
    assert resolution == "HIGH"


def test_compute_id_and_resolution_low_suffix():
    id_part, resolution = compute_id_and_resolution("abc123_low_resolution.csv")
    assert id_part == "abc123"
    assert resolution == "LOW"


def test_compute_id_and_resolution_trailing_underscore():
    id_part, resolution = compute_id_and_resolution("sensor__high_resolution.csv")
    # final trailing underscore must be stripped
    assert id_part == "sensor_"
    assert resolution == "HIGH"


def test_compute_id_and_resolution_assumes_high_when_unspecified(capsys):
    id_part, resolution = compute_id_and_resolution("foo.csv")

    assert id_part == "foo"
    assert resolution == "HIGH"

    out = capsys.readouterr().out
    assert "Assuming HIGH resolution" in out
    assert "foo.csv" in out


def test_compute_id_and_resolution_assumes_high_and_trims_underscore(capsys):
    id_part, resolution = compute_id_and_resolution("foo_.csv")

    assert id_part == "foo"
    assert resolution == "HIGH"

    out = capsys.readouterr().out
    assert "Assuming HIGH resolution" in out


# ---------- expand_file_patterns ----------


def test_expand_file_patterns(tmp_path: Path):
    f1 = tmp_path / "a_high_resolution.csv"
    f2 = tmp_path / "b_low_resolution.csv"
    f3 = tmp_path / "ignore.txt"

    f1.write_text("1,10\n")
    f2.write_text("2,20\n")
    f3.write_text("x")

    pattern = str(tmp_path / "*.csv")
    files = expand_file_patterns([pattern])

    assert set(files) == {str(f1), str(f2)}


def test_expand_file_patterns_warns_on_missing_pattern(capsys):
    # Just make sure it doesn't crash and prints a warning
    files = expand_file_patterns(["/path/that/does/not/exist/*.csv"])
    assert files == []

    out = capsys.readouterr().out
    assert "Warning: No files found matching pattern" in out


# ---------- import_csv_data + create_table (SQLite in-memory) ----------


def test_import_csv_data_basic_insert(tmp_path: Path):
    with sqlite_import_table() as (conn, cursor):
        csv_path = tmp_path / "device_high_resolution.csv"
        csv_path.write_text("1,10\n2,20\n")

        processed, skipped = import_csv_data(
            cursor=cursor,
            csv_file=str(csv_path),
            placeholder="?",
            id_val="device",
            resolution="HIGH",
            db_type=DatabaseType.SQLITE,
        )
        conn.commit()

        assert processed == 2
        assert skipped == 0

        rows = list(
            conn.execute(
                "SELECT id, resolution, timestamp, value "
                "FROM IMPORT_DATA ORDER BY timestamp"
            )
        )
        assert rows == [
            ("device", "HIGH", 1.0, 10.0),
            ("device", "HIGH", 2.0, 20.0),
        ]


def test_import_csv_data_skips_malformed_and_header(tmp_path: Path):
    with sqlite_import_table() as (conn, cursor):
        csv_path = tmp_path / "device_high_resolution.csv"
        # header + good + malformed (single column) + good
        csv_path.write_text("timestamp,value\n1,10\nbadline\n3,30\n")

        processed, skipped = import_csv_data(
            cursor=cursor,
            csv_file=str(csv_path),
            placeholder="?",
            id_val="device",
            resolution="HIGH",
            db_type=DatabaseType.SQLITE,
        )
        conn.commit()

        # 4 total lines, 2 valid rows
        assert processed == 2
        assert skipped == 2

        rows = list(
            conn.execute("SELECT timestamp, value FROM IMPORT_DATA ORDER BY timestamp")
        )
        assert rows == [
            (1.0, 10.0),
            (3.0, 30.0),
        ]


def test_import_csv_data_upsert_updates_existing_rows(tmp_path: Path):
    with sqlite_import_table() as (conn, cursor):
        csv_path = tmp_path / "device_high_resolution.csv"
        csv_path.write_text("1,10\n2,20\n")

        # First import
        import_csv_data(
            cursor=cursor,
            csv_file=str(csv_path),
            placeholder="?",
            id_val="device",
            resolution="HIGH",
            db_type=DatabaseType.SQLITE,
        )
        conn.commit()

        # Second import with updated values -> should use ON CONFLICT/UPSERT
        csv_path.write_text("1,15\n2,25\n")
        import_csv_data(
            cursor=cursor,
            csv_file=str(csv_path),
            placeholder="?",
            id_val="device",
            resolution="HIGH",
            db_type=DatabaseType.SQLITE,
        )
        conn.commit()

        rows = list(
            conn.execute("SELECT timestamp, value FROM IMPORT_DATA ORDER BY timestamp")
        )
        assert rows == [
            (1.0, 15.0),
            (2.0, 25.0),
        ]


def test_import_csv_data_mariadb_branch(tmp_path: Path):
    """
    Cover the MariaDB conflict clause branch in import_csv_data.
    We don't need a real DB, just a dummy cursor.
    """
    csv_path = tmp_path / "device_high_resolution.csv"
    csv_path.write_text("1,10\n2,20\n")

    cursor = DummyCursor()

    processed, skipped = import_csv_data(
        cursor=cursor,
        csv_file=str(csv_path),
        placeholder="%s",
        id_val="device",
        resolution="HIGH",
        db_type=DatabaseType.MARIADB,
    )

    assert processed == 2
    assert skipped == 0
    assert len(cursor.executed_queries) == 1
    # Ensure the ON DUPLICATE KEY UPDATE clause is present
    assert "ON DUPLICATE KEY UPDATE" in cursor.executed_queries[0]


def test_import_csv_data_unsupported_db_type_raises(tmp_path: Path):
    """Cover the defensive 'unsupported db type' branch."""
    with sqlite_import_table() as (conn, cursor):
        csv_path = tmp_path / "device_high_resolution.csv"
        csv_path.write_text("1,10\n")

        class FakeDb(Enum):
            OTHER = 1

        with pytest.raises(ValueError, match="Unsupported database type"):
            import_csv_data(
                cursor=cursor,
                csv_file=str(csv_path),
                placeholder="?",
                id_val="device",
                resolution="HIGH",
                db_type=FakeDb.OTHER,  # not SQLITE/MARIADB
            )


# ---------- create_table behavior (id / resolution constraints) ----------


def test_create_table_schema_allows_only_high_low_resolution():
    with sqlite_import_table() as (conn, cursor):
        # Insert valid resolutions
        cursor.execute(
            "INSERT INTO IMPORT_DATA (id, resolution, timestamp, value) "
            "VALUES ('s1', 'HIGH', 1.0, 10.0)"
        )
        cursor.execute(
            "INSERT INTO IMPORT_DATA (id, resolution, timestamp, value) "
            "VALUES ('s1', 'LOW', 2.0, 20.0)"
        )
        conn.commit()

        # Invalid resolution should fail CHECK constraint (in recent SQLite versions)
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO IMPORT_DATA (id, resolution, timestamp, value) "
                "VALUES ('s1', 'MED', 3.0, 30.0)"
            )
            conn.commit()


def test_create_table_no_recreate_keeps_existing_data():
    with sqlite_import_table() as (conn, cursor):
        # Table already created via sqlite_import_table()
        cursor.execute(
            "INSERT INTO IMPORT_DATA (id, resolution, timestamp, value) "
            "VALUES ('keep', 'HIGH', 1.0, 42.0)"
        )
        conn.commit()

        # Call create_table with recreate=False -> row should still be there
        create_table(cursor, recreate=False, verbose=False)
        conn.commit()

        rows = list(conn.execute("SELECT id, value FROM IMPORT_DATA"))
        assert rows == [("keep", 42.0)]


# ---------- log ----------


def test_log_verbose(capsys):
    log("hello", verbose=True)
    out = capsys.readouterr().out
    assert "hello" in out


def test_log_not_verbose(capsys):
    log("you should not see this", verbose=False)
    out = capsys.readouterr().out
    assert out == ""


# ---------- get_connection (SQLite + MariaDB) ----------


def test_get_connection_sqlite_missing_db_raises():
    args = argparse.Namespace(
        sqlite_db=None, user=None, database=None, password=None, host=None
    )
    with pytest.raises(ValueError, match="--sqlite-db is required"):
        get_connection(DatabaseType.SQLITE, args)


def test_get_connection_sqlite_ok(tmp_path: Path):
    db_path = tmp_path / "test.sqlite"
    args = argparse.Namespace(
        sqlite_db=str(db_path),
        user=None,
        database=None,
        password=None,
        host=None,
    )
    conn, placeholder = get_connection(DatabaseType.SQLITE, args)
    try:
        assert placeholder == "?"
        # Should be able to execute something simple
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
    finally:
        conn.close()


def test_get_connection_mariadb_missing_args_raises():
    # Missing user and database
    args = argparse.Namespace(
        sqlite_db=None,
        user=None,
        database=None,
        password=None,
        host="localhost",
    )
    with pytest.raises(
        ValueError, match="--user and --database are required for MariaDB"
    ):
        get_connection(DatabaseType.MARIADB, args)


def test_get_connection_mariadb_uses_connector(monkeypatch):
    # Fake mysql.connector via sys.modules so we don't need the real package installed
    called_kwargs = {}

    def fake_connect(**kwargs):
        called_kwargs.update(kwargs)
        # Return a dummy connection-like object
        return object()

    _install_fake_mysql(monkeypatch, fake_connect)

    args = argparse.Namespace(
        sqlite_db=None,
        user="user1",
        database="db1",
        password="secret",
        host="dbhost",
    )

    conn, placeholder = get_connection(DatabaseType.MARIADB, args)

    assert placeholder == "%s"
    assert conn is not None
    assert called_kwargs == {
        "host": "dbhost",
        "user": "user1",
        "password": "secret",
        "database": "db1",
    }


def test_get_connection_mariadb_default_empty_password(monkeypatch):
    """Cover the branch where password is None and defaults to empty string."""
    called_kwargs = {}

    def fake_connect(**kwargs):
        called_kwargs.update(kwargs)
        return object()

    _install_fake_mysql(monkeypatch, fake_connect)

    # password is None -> should default to ""
    args = argparse.Namespace(
        sqlite_db=None,
        user="user1",
        database="db1",
        password=None,
        host="dbhost",
    )

    conn, placeholder = get_connection(DatabaseType.MARIADB, args)

    assert placeholder == "%s"
    assert conn is not None
    assert called_kwargs["password"] == ""


def test_get_connection_unsupported_db_type_raises():
    """Cover the defensive 'unsupported database type' branch."""

    class FakeDb(Enum):
        OTHER = 1

    args = argparse.Namespace(
        sqlite_db=":memory:",
        user=None,
        database=None,
        password=None,
        host=None,
    )

    with pytest.raises(ValueError, match="Unsupported database type"):
        get_connection(FakeDb.OTHER, args)


# ---------- main() CLI behavior ----------


def test_main_requires_csv_or_cleanup(monkeypatch):
    # No --csv-file and no --cleanup-backup -> argparse error (SystemExit)
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--db-type", "sqlite", "--sqlite-db", ":memory:"],
    )
    with pytest.raises(SystemExit):
        main()


def test_main_cleanup_backup_sqlite(monkeypatch):
    # Just ensure it runs without error on SQLite and exits normally
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--db-type", "sqlite", "--sqlite-db", ":memory:", "--cleanup-backup"],
    )
    # Should not raise
    main()


def test_main_imports_csv_sqlite(tmp_path: Path, monkeypatch):
    # Real SQLite file so we can inspect after main() runs
    db_path = tmp_path / "importdata.sqlite"
    csv_path = tmp_path / "sensor_high_resolution.csv"
    csv_path.write_text("1,10\n2,20\n")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--db-type",
            "sqlite",
            "--sqlite-db",
            str(db_path),
            "--csv-file",
            str(csv_path),
        ],
    )

    # Run the full CLI path
    main()

    # Now inspect the DB
    conn = sqlite3.connect(str(db_path))
    try:
        rows = list(
            conn.execute(
                "SELECT id, resolution, timestamp, value "
                "FROM IMPORT_DATA ORDER BY timestamp"
            )
        )
    finally:
        conn.close()

    # compute_id_and_resolution should have used id 'sensor' and resolution 'HIGH'
    assert rows == [
        ("sensor", "HIGH", 1.0, 10.0),
        ("sensor", "HIGH", 2.0, 20.0),
    ]


def test_main_logs_error_for_no_matching_files(tmp_path: Path, monkeypatch, capsys):
    """
    Use a pattern that matches no CSVs -> main should hit the
    'No CSV files to process.' error path and log it.
    """
    db_path = tmp_path / "importdata.sqlite"
    pattern = str(tmp_path / "*.csv")  # no files created -> empty

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--db-type",
            "sqlite",
            "--sqlite-db",
            str(db_path),
            "--csv-file",
            pattern,
        ],
    )

    main()

    out = capsys.readouterr().out
    # Error path should mention 'No CSV files to process'
    assert "No CSV files to process" in out
    assert "An error occurred" in out


def test_main_logs_skipped_malformed_records(tmp_path: Path, monkeypatch, capsys):
    """Ensure the 'Skipped X malformed records' log line is executed."""
    db_path = tmp_path / "importdata_malformed.sqlite"
    csv_path = tmp_path / "sensor_high_resolution.csv"

    # Header + good row + malformed row + good row
    csv_path.write_text("timestamp,value\n1,10\nbadline\n3,30\n")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--db-type",
            "sqlite",
            "--sqlite-db",
            str(db_path),
            "--csv-file",
            str(csv_path),
            "--verbose",
        ],
    )

    main()

    out = capsys.readouterr().out
    assert "Skipped 2 malformed records from" in out

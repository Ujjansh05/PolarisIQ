# polaris_iq/cli/commands/tables.py

import typer
import duckdb
from polaris_iq.cli.display import (
    console, print_error, print_table_list, print_schema, print_info,
)


def tables(
    db_path: str = typer.Option(
        "polaris.db",
        "--db", "-d",
        help="Path to the DuckDB database file.",
    ),
    schema: str = typer.Option(
        None,
        "--schema", "-s",
        help="Show full schema for a specific table.",
    ),
):
    """List all tables in the PolarisIQ database, or inspect a specific table's schema."""

    try:
        conn = duckdb.connect(db_path, read_only=True)
    except Exception as e:
        print_error(f"Could not open database: {e}")
        raise typer.Exit(1)

    try:
        if schema:
            _show_schema(conn, schema)
        else:
            _list_tables(conn)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        conn.close()


def _list_tables(conn):
    rows = conn.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """).fetchall()

    if not rows:
        print_info("No tables found in the database.")
        return

    # Exclude internal polaris metadata tables from the main listing
    internal_tables = {"polaris_metadata", "polaris_statistics", "polaris_correlations", "execution_log"}

    table_data = []
    for (name,) in rows:
        if name in internal_tables:
            continue
        try:
            row_count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            col_count = len(conn.execute(f"DESCRIBE {name}").fetchall())
        except Exception:
            row_count = 0
            col_count = 0
        table_data.append((name, row_count, col_count))

    if not table_data:
        print_info("No user tables found. Use [bold]polarisiq ingest[/bold] to load data.")
        return

    print_table_list(table_data)

    # Also show internal tables count
    internal_count = sum(1 for (name,) in rows if name in internal_tables)
    if internal_count:
        console.print(f"  [muted]+{internal_count} internal metadata tables (polaris_metadata, polaris_statistics, ...)[/muted]")
        console.print()


def _show_schema(conn, table_name: str):
    try:
        cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
    except Exception:
        print_error(f"Table '{table_name}' not found.")
        raise typer.Exit(1)

    columns = []
    for col in cols:
        col_name = col[0]
        col_type = col[1]
        nullable = col[3] == "YES" if len(col) > 3 else True
        columns.append((col_name, col_type, nullable))

    print_schema(table_name, columns)

    # Row count
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    console.print(f"  [muted]Total rows: {row_count:,}[/muted]")
    console.print()

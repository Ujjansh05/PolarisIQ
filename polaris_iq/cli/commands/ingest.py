# polaris_iq/cli/commands/ingest.py

from pathlib import Path
import typer
from polaris_iq.cli.display import (
    console, print_success, print_error, print_info, create_progress,
)


def ingest(
    file_path: str = typer.Argument(..., help="Path to the data file to ingest."),
    table: str = typer.Option(
        None,
        "--table", "-t",
        help="Table name in DuckDB. Defaults to filename without extension.",
    ),
    db_path: str = typer.Option(
        "polaris.db",
        "--db", "-d",
        help="Path to the DuckDB database file.",
    ),
):
    """Ingest a data file into PolarisIQ (CSV, Parquet, JSON, Excel, DuckDB)."""

    path = Path(file_path)

    if not path.exists():
        print_error(f"File not found: {file_path}")
        raise typer.Exit(1)

    table_name = table or path.stem.replace(" ", "_").replace("-", "_").lower()

    print_info(f"Ingesting [bold]{path.name}[/bold] as table [bold cyan]{table_name}[/bold cyan]")

    progress = create_progress()

    with progress:
        task = progress.add_task("Loading and profiling data...", total=4)

        try:
            from polaris_iq.data_layer.precompute import precompute

            progress.update(task, advance=1, description=f"Reading {path.suffix} file...")
            precompute(
                input_path=str(path.resolve()),
                table_name=table_name,
                duckdb_path=db_path,
            )
            progress.update(task, advance=3, description="Done.")

        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_success(f"Table '{table_name}' ingested into {db_path}")

    # Show quick schema summary
    try:
        import duckdb
        conn = duckdb.connect(db_path)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        col_count = len(conn.execute(f"DESCRIBE {table_name}").fetchall())
        conn.close()
        console.print(f"  [muted]{row_count:,} rows, {col_count} columns[/muted]")
    except Exception:
        pass

    console.print()

# polaris_iq/cli/main.py

import typer
from polaris_iq.cli.display import print_banner

app = typer.Typer(
    name="polarisiq",
    help="PolarisIQ - AI-Driven Local Data Analytics Engine",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version", "-v",
        help="Show the PolarisIQ version and exit.",
    ),
):
    """
    [bold cyan]PolarisIQ[/bold cyan] - AI-Driven Local Data Analytics Engine.

    Convert natural language queries into structured data analysis,
    machine learning workflows, and visualizations — all running locally.
    """
    if version:
        from importlib.metadata import version as get_version

        try:
            v = get_version("polarisiq")
        except Exception:
            v = "0.1.0 (dev)"
        print_banner()
        typer.echo(f"  Version: {v}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        print_banner()


# ── Register commands ────────────────────────────────────────────

@app.command()
def ingest(
    file_path: str = typer.Argument(..., help="Path to the data file to ingest."),
    table: str = typer.Option(
        None,
        "--table", "-t",
        help="Table name in DuckDB. Defaults to filename stem.",
    ),
    db_path: str = typer.Option(
        "polaris.db",
        "--db", "-d",
        help="Path to the DuckDB database file.",
    ),
):
    """[bold]Ingest[/bold] a data file into PolarisIQ (CSV, Parquet, JSON, Excel)."""
    from polaris_iq.cli.commands.ingest import ingest as _ingest
    _ingest(file_path=file_path, table=table, db_path=db_path)


@app.command()
def query(
    user_query: str = typer.Argument(..., help="Natural language query about your data."),
    table: str = typer.Option(
        ...,
        "--table", "-t",
        help="Target table name.",
    ),
    model_path: str = typer.Option(
        None,
        "--model-path", "-m",
        help="Path to the GGUF model file.",
    ),
    db_path: str = typer.Option(
        None,
        "--db", "-d",
        help="Path to the DuckDB database file.",
    ),
    tool_mode: bool = typer.Option(
        False,
        "--tool",
        help="Use tool-based execution (plots, visualizations).",
    ),
):
    """[bold]Query[/bold] your data in natural language."""
    from polaris_iq.cli.commands.query import query as _query
    _query(
        user_query=user_query,
        table=table,
        model_path=model_path,
        db_path=db_path,
        tool_mode=tool_mode,
    )


@app.command(name="tables")
def tables_cmd(
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
    """[bold]List[/bold] all tables or inspect a table's schema."""
    from polaris_iq.cli.commands.tables import tables as _tables
    _tables(db_path=db_path, schema=schema)


@app.command(name="shell")
def shell_cmd(
    table: str = typer.Option(
        ...,
        "--table", "-t",
        help="Default table to query against.",
    ),
    model_path: str = typer.Option(
        None,
        "--model-path", "-m",
        help="Path to the GGUF model file.",
    ),
    db_path: str = typer.Option(
        None,
        "--db", "-d",
        help="Path to the DuckDB database file.",
    ),
):
    """[bold]Interactive REPL[/bold] for natural language analytics."""
    from polaris_iq.cli.commands.shell import shell as _shell
    _shell(table=table, model_path=model_path, db_path=db_path)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host."),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port."),
    reload: bool = typer.Option(False, "--reload", "-r", help="Auto-reload for dev."),
):
    """[bold]Start[/bold] the PolarisIQ API server for the web frontend."""
    from polaris_iq.cli.commands.serve import serve as _serve
    _serve(host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()

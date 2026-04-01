# polaris_iq/cli/commands/query.py

import time
import typer
from polaris_iq.cli.display import (
    console, print_error, print_query_result, print_section,
    create_progress, REASONING_STEPS,
)
from polaris_iq.cli.engine import resolve_model_path, resolve_db_path, bootstrap_engine


def query(
    user_query: str = typer.Argument(..., help="Natural language query about your data."),
    table: str = typer.Option(
        ...,
        "--table", "-t",
        help="Target table name in DuckDB.",
    ),
    model_path: str = typer.Option(
        None,
        "--model-path", "-m",
        help="Path to the GGUF model file. Can also set POLARISIQ_MODEL_PATH env var.",
    ),
    db_path: str = typer.Option(
        None,
        "--db", "-d",
        help="Path to the DuckDB database file.",
    ),
    tool_mode: bool = typer.Option(
        False,
        "--tool",
        help="Use tool-based execution mode (for plots, visualizations).",
    ),
):
    """Run a natural language query against your data."""

    resolved_model = resolve_model_path(model_path)
    resolved_db = resolve_db_path(db_path)

    print_section("Initializing PolarisIQ")

    try:
        orchestrator, engine = bootstrap_engine(resolved_model, resolved_db)
    except Exception as e:
        print_error(f"Failed to initialize engine: {e}")
        raise typer.Exit(1)

    print_section("Executing Query")
    console.print(f"  [dim]Query:[/dim] [bold white]{user_query}[/bold white]")
    console.print(f"  [dim]Table:[/dim] [cyan]{table}[/cyan]")
    console.print(f"  [dim]Mode:[/dim]  [cyan]{'tool' if tool_mode else 'deterministic'}[/cyan]")
    console.print()

    progress = create_progress()

    try:
        with progress:
            task = progress.add_task("Processing...", total=len(REASONING_STEPS))

            for i, step_label in enumerate(REASONING_STEPS):
                progress.update(task, advance=1, description=step_label)
                if i < len(REASONING_STEPS) - 1:
                    time.sleep(0.15)

            if tool_mode:
                result = orchestrator.handle_tool_query(user_query, table)
            else:
                result = orchestrator.handle_query(user_query, table)

            progress.update(task, description="Done.")

        print_section("Result")
        print_query_result(result)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        engine.shutdown()

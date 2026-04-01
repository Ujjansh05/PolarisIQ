# polaris_iq/cli/commands/shell.py

import typer
from polaris_iq.cli.display import (
    console, print_banner, print_success, print_error, print_info,
    print_query_result, print_section, print_muted,
)
from polaris_iq.cli.engine import resolve_model_path, resolve_db_path, bootstrap_engine


def shell(
    table: str = typer.Option(
        ...,
        "--table", "-t",
        help="Default table to query against.",
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
):
    """Start an interactive PolarisIQ REPL for natural language queries."""

    resolved_model = resolve_model_path(model_path)
    resolved_db = resolve_db_path(db_path)

    print_banner()
    print_section("Initializing Engine")

    try:
        orchestrator, engine = bootstrap_engine(resolved_model, resolved_db)
    except Exception as e:
        print_error(f"Failed to initialize engine: {e}")
        raise typer.Exit(1)

    print_success("Engine ready.")
    console.print()
    print_info(f"Table: [bold cyan]{table}[/bold cyan]")
    print_muted("Type your query in natural language. Commands: /tool, /table <name>, /quit")
    console.print()

    tool_mode = False

    try:
        while True:
            try:
                mode_tag = "[tool]" if tool_mode else ""
                prompt_text = console.input(f"[bold cyan]polarisiq[/bold cyan]{mode_tag} > ")
            except (EOFError, KeyboardInterrupt):
                console.print()
                break

            text = prompt_text.strip()

            if not text:
                continue

            # Handle commands
            if text.startswith("/"):
                cmd = text.lower().split()

                if cmd[0] in ("/quit", "/exit", "/q"):
                    break

                elif cmd[0] == "/tool":
                    tool_mode = not tool_mode
                    state = "ON" if tool_mode else "OFF"
                    print_info(f"Tool mode: [bold]{state}[/bold]")
                    continue

                elif cmd[0] == "/table" and len(cmd) > 1:
                    table = cmd[1]
                    print_info(f"Switched to table: [bold cyan]{table}[/bold cyan]")
                    continue

                elif cmd[0] == "/help":
                    _show_help()
                    continue

                else:
                    print_error(f"Unknown command: {cmd[0]}")
                    continue

            # Execute query
            try:
                with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
                    if tool_mode:
                        result = orchestrator.handle_tool_query(text, table)
                    else:
                        result = orchestrator.handle_query(text, table)

                print_query_result(result)

            except Exception as e:
                print_error(str(e))

    finally:
        engine.shutdown()
        print_muted("Session ended.")


def _show_help():
    console.print()
    console.print("[bold cyan]Shell Commands:[/bold cyan]")
    console.print("  [bold]/tool[/bold]          Toggle tool mode (for plots/visualizations)")
    console.print("  [bold]/table <name>[/bold]  Switch target table")
    console.print("  [bold]/help[/bold]          Show this help")
    console.print("  [bold]/quit[/bold]          Exit the shell")
    console.print()
    console.print("[dim]Type any natural language query to analyze your data.[/dim]")
    console.print()

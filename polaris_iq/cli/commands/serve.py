# polaris_iq/cli/commands/serve.py

import typer
from polaris_iq.cli.display import console, print_banner, print_info, print_error


def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host."),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port."),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development."),
):
    """Start the PolarisIQ API server (FastAPI + Uvicorn)."""

    try:
        import uvicorn
    except ImportError:
        print_error(
            "uvicorn is not installed.\n"
            "Install the API extras: [bold]pip install polarisiq[api][/bold]"
        )
        raise typer.Exit(1)

    print_banner()
    print_info(f"Starting API server on [bold]http://{host}:{port}[/bold]")
    console.print(f"  [muted]Press Ctrl+C to stop[/muted]")
    console.print()

    uvicorn.run(
        "polaris_iq.api.server:app",
        host=host,
        port=port,
        reload=reload,
    )

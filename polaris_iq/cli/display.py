# polaris_iq/cli/display.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.theme import Theme
from rich.rule import Rule


POLARIS_THEME = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "header": "bold magenta",
    "accent": "bold cyan",
    "muted": "dim white",
})

console = Console(theme=POLARIS_THEME)

BANNER_LINES = [
    "                                                                              ",
    "                                                                              ",
    "                                                                              ",
    "                                                                              ",
    "                                                                              ",
    "   ██████╗  ██████╗ ██╗      █████╗ ██████╗ ██╗███████╗    ██╗ ██████╗        ",
    "   ██╔══██╗██╔═══██╗██║     ██╔══██╗██╔══██╗██║██╔════╝    ██║██╔═══██╗       ",
    "   ██████╔╝██║   ██║██║     ███████║██████╔╝██║███████╗    ██║██║   ██║       ",
    "   ██╔═══╝ ██║   ██║██║     ██╔══██║██╔══██╗██║╚════██║    ██║██║▄▄ ██║       ",
    "   ██║     ╚██████╔╝███████╗██║  ██║██║  ██║██║███████║    ██║╚██████╔╝       ",
    "   ╚═╝      ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚═╝ ╚══▀▀═╝        ",
    "                                                                              ",
    "                                                                              ",
    "                                                                              ",
]

GRADIENT_COLORS = [
    "#0f172a",
    "#13203a",
    "#17294a",
    "#1b325a",
    "#1f3b6a",
    "#23447a",
    "#275d8a",
    "#2b769a",
    "#2f8faa",
    "#33a8ba",
    "#37c1ca",
]

def print_banner():
    console.print()

    banner_text = Text()
    for i, line in enumerate(BANNER_LINES):
        color = GRADIENT_COLORS[i % len(GRADIENT_COLORS)]
        banner_text.append(line + "\n", style=f"bold {color}")

    panel = Panel(
        banner_text,
        border_style="dim #4a5ced",
        padding=(0, 2),
        subtitle="[dim #88b0ff]AI-Driven Local Data Analytics Engine[/dim #88b0ff]",
        subtitle_align="center",
    )
    console.print(panel)

    # System info bar
    info = Text()
    info.append("  ◆ ", style="bold #6b82f6")
    info.append("v0.1.0", style="dim white")
    info.append("  │  ", style="dim #4a5ced")
    info.append("Engine: ", style="dim white")
    info.append("Qwen2.5 GGUF", style="#88b0ff")
    info.append("  │  ", style="dim #4a5ced")
    info.append("Runtime: ", style="dim white")
    info.append("DuckDB + Polars + Sklearn", style="#88b0ff")
    info.append("  │  ", style="dim #4a5ced")
    info.append("Local ", style="#6b82f6")
    info.append("●", style="bold green")
    console.print(info, justify="center")
    console.print()


def print_success(message: str):
    console.print(f"[success]{message}[/success]")


def print_error(message: str):
    console.print(f"[error]Error:[/error] {message}")


def print_warning(message: str):
    console.print(f"[warning]Warning:[/warning] {message}")


def print_info(message: str):
    console.print(f"[info]{message}[/info]")


def print_muted(message: str):
    console.print(f"[muted]{message}[/muted]")


def print_section(title: str):
    console.print()
    console.print(Rule(title, style="cyan"))
    console.print()


def print_query_result(result: dict):
    """Display a query result with engine metadata and explanation."""

    explanation = result.get("explanation", "")
    metadata = result.get("metadata", {})
    tool_result = result.get("tool_result", None)

    if tool_result:
        console.print(Panel(
            str(tool_result),
            title="[accent]Tool Result[/accent]",
            border_style="cyan",
            padding=(1, 2),
        ))
        if metadata:
            _print_metadata_tags(metadata)
        return

    console.print(Panel(
        Markdown(str(explanation)) if explanation else Text("No explanation returned.", style="muted"),
        title="[accent]PolarisIQ Response[/accent]",
        border_style="cyan",
        padding=(1, 2),
    ))

    if metadata:
        _print_metadata_tags(metadata)


def _print_metadata_tags(metadata: dict):
    tags = Table(show_header=False, show_edge=False, box=None, padding=(0, 2))
    tags.add_column("key", style="dim")
    tags.add_column("value", style="bold cyan")

    for key, value in metadata.items():
        tags.add_row(key, str(value))

    console.print(tags)
    console.print()


def print_table_list(tables: list[tuple]):
    """Display a list of tables with row counts."""

    table = Table(
        title="Loaded Tables",
        title_style="bold cyan",
        border_style="dim cyan",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Table Name", style="bold white")
    table.add_column("Rows", style="cyan", justify="right")
    table.add_column("Columns", style="cyan", justify="right")

    for idx, (name, rows, cols) in enumerate(tables, 1):
        table.add_row(str(idx), name, str(rows), str(cols))

    console.print()
    console.print(table)
    console.print()


def print_schema(table_name: str, columns: list[tuple]):
    """Display table schema."""

    table = Table(
        title=f"Schema: {table_name}",
        title_style="bold cyan",
        border_style="dim cyan",
        show_lines=True,
    )
    table.add_column("Column", style="bold white")
    table.add_column("Type", style="cyan")
    table.add_column("Nullable", style="dim")

    for col_name, col_type, nullable in columns:
        table.add_row(col_name, col_type, "yes" if nullable else "no")

    console.print()
    console.print(table)
    console.print()


def create_progress():
    return Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30, style="dim cyan", complete_style="cyan"),
        console=console,
    )


REASONING_STEPS = [
    "Understanding natural language query",
    "Mapping entities to hybrid OLAP schema",
    "Generating optimized execution plan",
    "Selecting best execution engine",
    "Executing query pipeline",
    "Generating explanation",
]

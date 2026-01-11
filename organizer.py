#!/usr/bin/env python3
"""
AI-Powered File Organizer

An intelligent file organizer that uses a local LLM (Ollama) to analyze
file contents and organize them into meaningful categories.
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich import box

from config import Config, DEFAULT_CONFIG
from scanner import FileScanner, FileInfo
from analyzer import FileAnalyzer, AnalysisResult
from mover import FileMover, MoveOperation
from categories import get_all_categories


console = Console()


def print_banner():
    """Print the application banner."""
    banner = Text()
    banner.append("AI File Organizer", style="bold cyan")
    banner.append(" - Intelligent file organization powered by local LLM", style="dim")
    console.print(Panel(banner, box=box.ROUNDED))


def print_categories():
    """Print available categories."""
    table = Table(title="Available Categories", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Description", style="dim")

    for category in get_all_categories():
        table.add_row(category.name, category.path, category.description)

    console.print(table)


def scan_files(source_dir: Path, config: Config, recursive: bool = True) -> list[FileInfo]:
    """Scan directory for files."""
    console.print(f"\n[bold]Scanning:[/bold] {source_dir}" + (" (recursive)" if recursive else " (top-level only)"))

    scanner = FileScanner(config)
    files = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Discovering files...", total=None)
        for file_info in scanner.scan_directory(source_dir, recursive=recursive):
            files.append(file_info)
            progress.update(task, description=f"Found {len(files)} files...")

    console.print(f"[green]Found {len(files)} files to organize[/green]\n")
    return files


def analyze_files(files: list[FileInfo], config: Config, fast_mode: bool = False) -> list[AnalysisResult]:
    """Analyze files and determine categories."""
    analyzer = FileAnalyzer(config)

    # Check Ollama status
    if fast_mode:
        console.print("[cyan]Fast mode[/cyan] - using extension/keyword matching only")
        analyzer._ollama_available = False  # Disable AI in fast mode
    elif analyzer.ollama_available:
        console.print(f"[green]Ollama connected[/green] - using model: {config.ollama_model}")
    else:
        console.print("[yellow]Ollama not available[/yellow] - using rule-based classification")

    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing files...", total=len(files))

        for file_info in files:
            result = analyzer.analyze_file(file_info)
            results.append(result)
            progress.update(task, advance=1, description=f"Analyzing: {file_info.name[:40]}...")

    # Summary of analysis methods
    methods = {}
    for r in results:
        methods[r.method] = methods.get(r.method, 0) + 1

    console.print("\n[bold]Analysis Summary:[/bold]")
    for method, count in sorted(methods.items(), key=lambda x: -x[1]):
        icon = {"ai": "[cyan]AI[/cyan]", "extension": "[green]Ext[/green]",
                "keyword": "[yellow]Key[/yellow]", "fallback": "[red]Fallback[/red]"}.get(method, method)
        console.print(f"  {icon}: {count} files")

    return results


def display_plan(results: list[AnalysisResult], output_dir: Path):
    """Display the organization plan in a table."""
    table = Table(title="Organization Plan", box=box.ROUNDED, show_lines=True)
    table.add_column("File", style="cyan", max_width=35)
    table.add_column("Category", style="green")
    table.add_column("Destination", style="yellow", max_width=40)
    table.add_column("Method", style="dim")
    table.add_column("Confidence", justify="right")

    for result in results:
        dest_path = output_dir / result.category.path / result.file_info.name
        conf_style = "green" if result.confidence >= 0.8 else "yellow" if result.confidence >= 0.5 else "red"

        table.add_row(
            result.file_info.name,
            result.category.name,
            str(dest_path.relative_to(output_dir)),
            result.method,
            f"[{conf_style}]{result.confidence:.0%}[/{conf_style}]"
        )

    console.print(table)


def organize_files(results: list[AnalysisResult], output_dir: Path, config: Config, dry_run: bool) -> tuple[list[MoveOperation], int]:
    """Move files to their organized locations."""
    mover = FileMover(output_dir, config, dry_run=dry_run)
    source_dir = results[0].file_info.path.parent if results else Path(".")

    mover.start_session(source_dir)
    operations = []
    skipped = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Organizing files...", total=len(results))

        for result in results:
            operation = mover.move_file(result)
            if operation:
                operations.append(operation)
            else:
                skipped += 1
            progress.update(task, advance=1, description=f"Moving: {result.file_info.name[:40]}...")

    mover.end_session()
    return operations, skipped


def undo_organization(output_dir: Path, config: Config):
    """Undo the last organization session."""
    console.print("\n[bold]Undoing last organization...[/bold]")

    mover = FileMover(output_dir, config)
    success, message, moves = mover.undo_last_session()

    if success:
        console.print(f"[green]{message}[/green]")
        if moves:
            table = Table(title="Restored Files", box=box.ROUNDED)
            table.add_column("From", style="yellow")
            table.add_column("To", style="green")

            for src, dst in moves[:20]:  # Show first 20
                table.add_row(Path(src).name, dst)

            if len(moves) > 20:
                table.add_row("...", f"and {len(moves) - 20} more files")

            console.print(table)
    else:
        console.print(f"[red]{message}[/red]")

    return success


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered File Organizer - Organize your files intelligently using local LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/Downloads                    # Organize Downloads folder
  %(prog)s ~/Downloads --dry-run          # Preview without moving files
  %(prog)s ~/Downloads --output ~/Sorted  # Custom output directory
  %(prog)s --undo                         # Undo last organization
  %(prog)s --categories                   # List all categories
        """
    )

    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Directory to organize"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output directory for organized files (default: source/Organized)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview changes without moving files"
    )
    parser.add_argument(
        "--undo", "-u",
        action="store_true",
        help="Undo the last organization session"
    )
    parser.add_argument(
        "--model", "-m",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)"
    )
    parser.add_argument(
        "--categories", "-c",
        action="store_true",
        help="List all available categories"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=True,
        help="Scan subdirectories (default: True)"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Don't scan subdirectories"
    )
    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        help="Fast mode: skip AI analysis, use only extension/keyword matching"
    )

    args = parser.parse_args()

    print_banner()

    # Handle --categories flag
    if args.categories:
        print_categories()
        return 0

    # Handle --undo flag
    if args.undo:
        output_dir = args.output or Path.cwd() / DEFAULT_CONFIG.output_dir_name
        return 0 if undo_organization(output_dir, DEFAULT_CONFIG) else 1

    # Require source directory for organization
    if not args.source:
        parser.print_help()
        console.print("\n[red]Error: Please specify a source directory to organize[/red]")
        return 1

    source_dir = args.source.expanduser().resolve()
    if not source_dir.exists():
        console.print(f"[red]Error: Source directory does not exist: {source_dir}[/red]")
        return 1

    if not source_dir.is_dir():
        console.print(f"[red]Error: Source path is not a directory: {source_dir}[/red]")
        return 1

    # Setup output directory
    output_dir = args.output.expanduser().resolve() if args.output else source_dir / DEFAULT_CONFIG.output_dir_name

    # Setup config
    config = Config(ollama_model=args.model)

    # Mode indicator
    if args.dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be moved[/yellow]\n")
    if args.fast:
        console.print("[cyan]FAST MODE - Skipping AI analysis[/cyan]\n")

    # Step 1: Scan files
    files = scan_files(source_dir, config, recursive=args.recursive)
    if not files:
        console.print("[yellow]No files found to organize[/yellow]")
        return 0

    # Step 2: Analyze files
    results = analyze_files(files, config, fast_mode=args.fast)

    # Step 3: Display plan
    console.print()
    display_plan(results, output_dir)

    # Step 4: Execute (or preview)
    if args.dry_run:
        console.print("\n[yellow]Dry run complete. Use without --dry-run to organize files.[/yellow]")
    else:
        console.print()
        operations, skipped = organize_files(results, output_dir, config, dry_run=False)

        # Summary
        console.print(f"\n[bold green]Organization complete![/bold green]")
        console.print(f"  Organized [cyan]{len(operations)}[/cyan] files into [cyan]{output_dir}[/cyan]")
        if skipped > 0:
            console.print(f"  Skipped [yellow]{skipped}[/yellow] files (permission denied)")
        console.print(f"  Use [yellow]--undo[/yellow] to reverse this operation")

    return 0


if __name__ == "__main__":
    sys.exit(main())

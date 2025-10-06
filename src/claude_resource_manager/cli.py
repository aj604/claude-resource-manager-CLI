"""
Claude Resource Manager CLI

Main entry point for CLI commands using Click framework.
Provides commands: browse, install, search, deps, sync

Security: All file operations validated, HTTPS-only downloads
Performance: <100ms startup target with lazy imports
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

# Lazy imports for performance (only import when needed)
console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Minimize output")
@click.option(
    "--catalog-path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Custom catalog path",
)
@click.pass_context
def cli(ctx, version, verbose, quiet, catalog_path):
    """
    Claude Resource Manager CLI - Manage Claude resources interactively

    \b
    Examples:
      crm browse              # Launch interactive TUI
      crm search "architect"  # Search resources
      crm install architect   # Install resource
      crm deps architect      # Show dependencies
      crm sync                # Update catalog
    """
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["catalog_path"] = catalog_path or Path.home() / ".claude" / "registry" / "catalog"

    if version:
        from claude_resource_manager import __version__

        click.echo(f"claude-resource-manager version {__version__}")
        ctx.exit(0)

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option("--type", "-t", help="Filter by resource type (agent, command, hook, template, mcp)")
@click.option("--category", "-c", help="Filter by category")
@click.pass_context
def browse(ctx, type, category):
    """
    Launch interactive TUI browser

    Navigate resources with keyboard:
      ↑↓ - Navigate list
      / - Search
      Space - Toggle selection
      Enter - View details
      i - Install selected
      q - Quit
    """
    try:
        from claude_resource_manager.tui.app import launch_tui

        launch_tui(
            catalog_path=ctx.obj["catalog_path"],
            resource_type=type,
            category=category,
            verbose=ctx.obj["verbose"],
        )
    except Exception as e:
        if ctx.obj["verbose"]:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("resource_id")
@click.option("--with-deps/--no-deps", default=True, help="Install with dependencies")
@click.option("--force", "-f", is_flag=True, help="Force overwrite if exists")
@click.option("--dry-run", is_flag=True, help="Show what would be installed")
@click.pass_context
def install(ctx, resource_id, with_deps, force, dry_run):
    """
    Install a resource by ID

    \b
    Examples:
      claude-resources install architect
      claude-resources install architect --no-deps
      claude-resources install architect --force
      claude-resources install architect --dry-run
    """
    try:

        # Run async installation
        asyncio.run(
            _install_async(
                resource_id=resource_id,
                catalog_path=ctx.obj["catalog_path"],
                with_deps=with_deps,
                force=force,
                dry_run=dry_run,
                verbose=ctx.obj["verbose"],
                quiet=ctx.obj["quiet"],
            )
        )

    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Catalog not found at {ctx.obj['catalog_path']}")
        console.print("[yellow]Hint:[/yellow] Run 'claude-resources sync' to download catalog")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print(
            f"[yellow]Hint:[/yellow] Resource '{resource_id}' not found. Try 'claude-resources search {resource_id}'"
        )
        sys.exit(1)
    except Exception as e:
        if ctx.obj["verbose"]:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


async def _install_async(
    resource_id: str,
    catalog_path: Path,
    with_deps: bool,
    force: bool,
    dry_run: bool,
    verbose: bool,
    quiet: bool,
):
    """Async installation helper"""
    from claude_resource_manager.core.catalog_loader import CatalogLoader
    from claude_resource_manager.core.installer import AsyncInstaller

    # Load catalog
    loader = CatalogLoader(catalog_path)

    if not quiet:
        with console.status("[cyan]Loading catalog..."):
            await loader.load_index()
    else:
        await loader.load_index()

    # Find resource
    resource = await loader.load_resource(resource_id)

    if resource is None:
        raise ValueError(f"Resource '{resource_id}' not found in catalog")

    # Install
    installer = AsyncInstaller(base_path=Path.home() / ".claude")

    if with_deps and resource.dependencies:
        # Resolve dependencies
        if not quiet:
            console.print(f"[cyan]Resolving dependencies for {resource_id}...")

        # TODO: Implement dependency resolution
        # For now, just install the resource

    if dry_run:
        console.print(f"[yellow]Would install:[/yellow] {resource_id}")
        if with_deps and resource.dependencies:
            console.print(f"[yellow]With dependencies:[/yellow] {resource.dependencies}")
        return

    # Perform installation
    if not quiet:
        console.print(f"[cyan]Installing {resource_id}...")

    result = await installer.install(resource, force=force)

    if result.get("success"):
        if not quiet:
            console.print(f"[green]✓[/green] Successfully installed {resource_id}")
            console.print(f"  [dim]Path:[/dim] {result.get('path')}")
    else:
        console.print(f"[red]✗[/red] Failed to install {resource_id}")
        console.print(f"  [dim]Error:[/dim] {result.get('error')}")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--type", "-t", help="Filter by resource type")
@click.option("--limit", "-n", type=int, default=20, help="Maximum results")
@click.option("--fuzzy/--exact", default=True, help="Fuzzy vs exact search")
@click.pass_context
def search(ctx, query, type, limit, fuzzy):
    """
    Search resources by name or description

    \b
    Examples:
      claude-resources search architect
      claude-resources search database --type agent
      claude-resources search "code review" --limit 10
      claude-resources search test --exact
    """
    try:

        asyncio.run(
            _search_async(
                query=query,
                catalog_path=ctx.obj["catalog_path"],
                resource_type=type,
                limit=limit,
                fuzzy=fuzzy,
                verbose=ctx.obj["verbose"],
                quiet=ctx.obj["quiet"],
            )
        )

    except Exception as e:
        if ctx.obj["verbose"]:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


async def _search_async(
    query: str,
    catalog_path: Path,
    resource_type: Optional[str],
    limit: int,
    fuzzy: bool,
    verbose: bool,
    quiet: bool,
):
    """Async search helper"""
    from claude_resource_manager.core.catalog_loader import CatalogLoader
    from claude_resource_manager.core.search_engine import SearchEngine

    # Load catalog
    loader = CatalogLoader(catalog_path)

    if not quiet:
        with console.status("[cyan]Searching..."):
            all_resources = await loader.load_all_resources()
    else:
        all_resources = await loader.load_all_resources()

    # Build search index
    engine = SearchEngine()
    for resource in all_resources:
        engine.add_resource(resource)

    # Search
    mode = "fuzzy" if fuzzy else "exact"
    results = engine.search(query, mode=mode)

    # Filter by type if specified
    if resource_type:
        results = [r for r in results if r.type == resource_type]

    # Limit results
    results = results[:limit]

    # Display results
    if not results:
        console.print(f"[yellow]No results found for:[/yellow] '{query}'")
        if resource_type:
            console.print(f"  [dim]Type filter:[/dim] {resource_type}")
        return

    # Create table
    table = Table(title=f"Search Results ({len(results)} found)")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Name", style="white")
    table.add_column("Description", style="dim")

    for result in results:
        # Truncate description
        desc = result.description
        if len(desc) > 60:
            desc = desc[:57] + "..."

        table.add_row(result.id, result.type, result.name, desc)

    console.print(table)

    if verbose:
        console.print(f"\n[dim]Search mode:[/dim] {mode}")
        console.print(f"[dim]Total results:[/dim] {len(results)}")


@cli.command()
@click.argument("resource_id")
@click.option("--reverse", "-r", is_flag=True, help="Show what depends on this resource")
@click.option("--tree", "-t", is_flag=True, help="Display as tree")
@click.pass_context
def deps(ctx, resource_id, reverse, tree):
    """
    Show dependency tree for a resource

    \b
    Examples:
      claude-resources deps architect
      claude-resources deps architect --reverse
      claude-resources deps architect --tree
    """
    try:

        asyncio.run(
            _deps_async(
                resource_id=resource_id,
                catalog_path=ctx.obj["catalog_path"],
                reverse=reverse,
                show_tree=tree,
                verbose=ctx.obj["verbose"],
            )
        )

    except Exception as e:
        if ctx.obj["verbose"]:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


async def _deps_async(
    resource_id: str, catalog_path: Path, reverse: bool, show_tree: bool, verbose: bool
):
    """Async dependency resolution helper"""
    from claude_resource_manager.core.catalog_loader import CatalogLoader

    # Load catalog
    loader = CatalogLoader(catalog_path)
    resource = await loader.load_resource(resource_id)

    if resource is None:
        raise ValueError(f"Resource '{resource_id}' not found")

    if reverse:
        # Show what depends on this resource (reverse dependencies)
        console.print(f"[cyan]Resources that depend on {resource_id}:[/cyan]")
        console.print("[yellow]Not implemented yet[/yellow]")
    else:
        # Show dependencies
        if resource.dependencies:
            if show_tree:
                # Tree view
                tree_view = Tree(f"[cyan]{resource_id}[/cyan]")

                if resource.dependencies.required:
                    required_branch = tree_view.add("[red]Required[/red]")
                    for dep in resource.dependencies.required:
                        required_branch.add(f"[white]{dep}[/white]")

                if resource.dependencies.recommended:
                    recommended_branch = tree_view.add("[yellow]Recommended[/yellow]")
                    for dep in resource.dependencies.recommended:
                        recommended_branch.add(f"[dim]{dep}[/dim]")

                console.print(tree_view)
            else:
                # List view
                console.print(f"[cyan]Dependencies for {resource_id}:[/cyan]\n")

                if resource.dependencies.required:
                    console.print("[red]Required:[/red]")
                    for dep in resource.dependencies.required:
                        console.print(f"  • {dep}")

                if resource.dependencies.recommended:
                    console.print("\n[yellow]Recommended:[/yellow]")
                    for dep in resource.dependencies.recommended:
                        console.print(f"  • {dep}")
        else:
            console.print(f"[dim]{resource_id} has no dependencies[/dim]")


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Force full sync")
@click.pass_context
def sync(ctx, force):
    """
    Update resource catalog from GitHub sources

    Runs the Node.js sync.js script to fetch latest resources
    from configured GitHub repositories.
    """
    try:
        import subprocess
        from pathlib import Path

        # Find sync.js in parent repository
        project_root = Path(__file__).parent.parent.parent
        sync_script = project_root.parent / "claude_resource_manager" / "scripts" / "sync.js"

        if not sync_script.exists():
            console.print(f"[red]Error:[/red] sync.js not found at {sync_script}")
            console.print(
                "[yellow]Hint:[/yellow] Ensure claude_resource_manager repository is cloned"
            )
            sys.exit(1)

        console.print("[cyan]Syncing resource catalog...[/cyan]")

        # Run Node.js sync script
        cmd = ["node", str(sync_script)]
        if force:
            cmd.append("--force")

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sync_script.parent.parent)

        if result.returncode == 0:
            console.print("[green]✓[/green] Catalog synced successfully")
            if ctx.obj["verbose"]:
                console.print(result.stdout)
        else:
            console.print("[red]✗[/red] Sync failed")
            console.print(result.stderr)
            sys.exit(1)

    except FileNotFoundError:
        console.print("[red]Error:[/red] Node.js not found")
        console.print("[yellow]Hint:[/yellow] Install Node.js to sync catalog")
        sys.exit(1)
    except Exception as e:
        if ctx.obj["verbose"]:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


def main():
    """Entry point for CLI"""
    cli(obj={})


if __name__ == "__main__":
    main()

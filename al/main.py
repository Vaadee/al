"""Main entry point for the al CLI."""

import os
import re
import subprocess
from pathlib import Path

import questionary
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from al.core.config import config
from al.core.constants import RESERVED_ALIASES
from al.core.parser import Alias, parse_aliases, serialize_aliases
from al.core.shell import ensure_shell_source, is_initialized
from al.core.sync import GistSync

app = typer.Typer(help="al - Alias Manager", no_args_is_help=True)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print("al version 0.1.0")
        raise typer.Exit


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit.",
    ),
) -> None:
    """Entry point for all commands."""
    if ctx.invoked_subcommand in ["init", "help", "check", None]:
        return

    # Check if initialized
    if not is_initialized():
        console.print(
            "[red]al is not initialized. Please run 'al init' first.[/red]",
        )
        raise typer.Exit(code=1)


@app.command()
def help(ctx: typer.Context) -> None:
    """Show this message and exit."""
    console.print(ctx.parent.get_help())


@app.command()
def check() -> None:
    """Check the health of the al installation."""
    table = Table(title="System Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    # 1. Config Directory
    if config.config_dir.exists():
        table.add_row("Config Directory", "✅", str(config.config_dir))
    else:
        table.add_row("Config Directory", "❌", "Not found")

    # 2. Alias File
    if config.alias_file.exists():
        table.add_row("Alias File", "✅", str(config.alias_file))
    else:
        table.add_row("Alias File", "❌", "Not found")

    # 3. Shell RC
    rc_file = config.shell_rc
    if rc_file:
        if rc_file.exists():
            table.add_row("Shell Configuration", "✅", str(rc_file))
        else:
            table.add_row("Shell Configuration", "❌", f"File not found: {rc_file}")
    else:
        table.add_row("Shell Configuration", "❌", "Could not detect shell")

    # 4. Initialization
    if is_initialized():
        table.add_row("Initialization", "✅", "Sourced in shell rc")
    else:
        table.add_row("Initialization", "❌", "Not sourced")

    console.print(table)


@app.command()
def init() -> None:
    """Initialize al: create config and add source to shell rc.

    Examples:
        $ al init

    """
    config._ensure_config_dir()
    success, msg = ensure_shell_source()
    if success:
        console.print(f"[green]{msg}[/green]")
        console.print(
            f"[yellow]Please run 'source {config.shell_rc}' "
            "or restart your terminal to apply changes.[/yellow]",
        )
    else:
        console.print(f"[red]{msg}[/red]")


@app.command()
def add() -> None:
    """Interactively add a new alias.

    Examples:
        $ al add

    """
    # Read existing
    if config.alias_file.exists():
        content = config.alias_file.read_text()
        groups = parse_aliases(content)
    else:
        groups = {"main": []}

    # Get group options
    group_options = [*list(groups.keys()), "Create new group"]

    group = questionary.select(
        "Select group:",
        choices=group_options,
    ).ask()

    if group == "Create new group":
        group = questionary.text("Enter new group name:").ask()
        if not group:
            console.print("[red]Group name cannot be empty[/red]")
            return

    name = questionary.text("Alias name:").ask()
    if not name:
        console.print("[red]Alias name cannot be empty[/red]")
        return

    if name in RESERVED_ALIASES:
        console.print(f"[red]Alias name '{name}' is reserved.[/red]")
        return

    command = questionary.text("Command:").ask()
    if not command:
        console.print("[red]Command cannot be empty[/red]")
        return

    # Add to group
    if group not in groups:
        groups[group] = []

    # Check if exists in group
    for a in groups[group]:
        if a.name == name:
            if not questionary.confirm(
                f"Alias '{name}' already exists in '{group}'. Overwrite?",
            ).ask():
                return
            groups[group].remove(a)
            break

    groups[group].append(Alias(name=name, command=command, group=group))

    # Save
    new_content = serialize_aliases(groups)
    config.alias_file.write_text(new_content)
    console.print(f"[green]Alias '{name}' added to group '{group}'[/green]")
    console.print(f"[dim]Run 'source {config.shell_rc}' to apply[/dim]")


@app.command()
def view(group: str | None = typer.Argument(None, help="Filter by group name")) -> None:
    """List all aliases, optionally filtered by group.

    Examples:
        $ al view
        $ al view dev

    """
    if not config.alias_file.exists():
        console.print("[yellow]No aliases found. Run 'al add' to create one.[/yellow]")
        return

    content = config.alias_file.read_text()
    groups = parse_aliases(content)

    table = Table(title="Aliases")
    table.add_column("Group", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Command")

    for g_name, aliases in groups.items():
        if group and group != g_name:
            continue

        for alias in aliases:
            syntax = Syntax(alias.command, "bash", theme="monokai", word_wrap=True)
            table.add_row(g_name, alias.name, syntax)

    console.print(table)


@app.command(name="list")
def list_aliases(
    group: str | None = typer.Argument(None, help="Filter by group name"),
) -> None:
    """Alias for 'view'.

    Examples:
        $ al list
        $ al list dev

    """
    view(group)


@app.command()
def search(query: str) -> None:
    """Search aliases by name or command.

    Examples:
        $ al search docker
        $ al search "git log"

    """
    if not config.alias_file.exists():
        console.print("[yellow]No aliases found.[/yellow]")
        return

    content = config.alias_file.read_text()
    groups = parse_aliases(content)

    table = Table(title=f"Search Results: '{query}'")
    table.add_column("Group", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Command")

    found = False
    for g_name, aliases in groups.items():
        for alias in aliases:
            if (
                query.lower() in alias.name.lower()
                or query.lower() in alias.command.lower()
            ):
                syntax = Syntax(alias.command, "bash", theme="monokai", word_wrap=True)
                table.add_row(g_name, alias.name, syntax)
                found = True

    if found:
        console.print(table)
    else:
        console.print(f"[yellow]No matches found for '{query}'[/yellow]")


@app.command()
def run(name: str) -> None:
    """Run an alias by name.

    Examples:
        $ al run my-alias

    """
    if not config.alias_file.exists():
        console.print("[yellow]No aliases found.[/yellow]")
        return

    content = config.alias_file.read_text()
    groups = parse_aliases(content)

    # Find alias
    target_alias = None
    for aliases in groups.values():
        for alias in aliases:
            if alias.name == name:
                target_alias = alias
                break
        if target_alias:
            break

    if not target_alias:
        console.print(f"[red]Alias '{name}' not found.[/red]")
        return

    console.print(f"[dim]Running: {target_alias.command}[/dim]")
    subprocess.run(target_alias.command, shell=True, check=False)


@app.command(name="import")
def import_aliases(
    file_path: Path = typer.Argument(
        ...,
        help="Path to file to import from (e.g. .zshrc)",
    ),
) -> None:
    """Import aliases from a file (e.g. .zshrc, .bash_aliases).

    Examples:
        $ al import ~/.zshrc
        $ al import ~/.bash_aliases

    """
    if not file_path.exists():
        console.print(f"[red]File {file_path} does not exist.[/red]")
        return

    content = file_path.read_text()
    imported_count = 0

    # Simple regex for standard alias format: alias name='command'
    # This ignores groups and just looks for alias lines
    matches = re.finditer(
        r"^alias\s+([\w\.-]+)=[\"'](.*)[\"']$",
        content,
        re.MULTILINE,
    )

    if config.alias_file.exists():
        current_content = config.alias_file.read_text()
        groups = parse_aliases(current_content)
    else:
        groups = {"main": []}

    target_group = "imported"
    if target_group not in groups:
        groups[target_group] = []

    for match in matches:
        name = match.group(1)
        command = match.group(2)

        # Check duplicates in imported group
        exists = False
        for a in groups[target_group]:
            if a.name == name:
                exists = True
                break

        if not exists:
            groups[target_group].append(
                Alias(name=name, command=command, group=target_group),
            )
            imported_count += 1

    if imported_count > 0:
        new_content = serialize_aliases(groups)
        config.alias_file.write_text(new_content)
        console.print(
            f"[green]Imported {imported_count} aliases into group "
            f"'{target_group}'[/green]",
        )
    else:
        console.print("[yellow]No new aliases found to import.[/yellow]")


@app.command()
def sync(action: str = typer.Argument(..., help="Action: 'push' or 'pull'")) -> None:
    """Sync aliases with GitHub Gist.

    Examples:
        $ al sync push
        $ al sync pull

    """
    sync_config = config.load_sync_config()
    token = sync_config.get("token")

    if not token:
        console.print("[yellow]GitHub Token not found.[/yellow]")
        token = questionary.password(
            "Enter GitHub Personal Access Token (with gist scope):",
        ).ask()
        if not token:
            return
        sync_config["token"] = token
        config.save_sync_config(sync_config)

    syncer = GistSync(token)

    if action == "push":
        if not config.alias_file.exists():
            console.print("[red]No aliases to push.[/red]")
            return

        content = config.alias_file.read_text()
        gist_id = sync_config.get("gist_id")

        with console.status("Pushing to Gist..."):
            success, result = syncer.push(content, gist_id)

        if success:
            console.print(f"[green]Successfully pushed to Gist: {result}[/green]")
            if gist_id != result:
                sync_config["gist_id"] = result
                config.save_sync_config(sync_config)
        else:
            console.print(f"[red]Push failed: {result}[/red]")

    elif action == "pull":
        gist_id = sync_config.get("gist_id")
        if not gist_id:
            gist_id = questionary.text("Enter Gist ID to pull from:").ask()
            if not gist_id:
                return

        with console.status("Pulling from Gist..."):
            success, result = syncer.pull(gist_id)

        if success:
            # Backup existing
            if config.alias_file.exists():
                backup = config.alias_file.with_suffix(".bak")
                config.alias_file.rename(backup)
                console.print(f"[dim]Backed up existing aliases to {backup}[/dim]")

            config.alias_file.write_text(result)
            console.print("[green]Successfully pulled aliases from Gist.[/green]")

            # Save gist_id if we just entered it
            if sync_config.get("gist_id") != gist_id:
                sync_config["gist_id"] = gist_id
                config.save_sync_config(sync_config)
        else:
            console.print(f"[red]Pull failed: {result}[/red]")
    else:
        console.print(f"[red]Unknown action: {action}. Use 'push' or 'pull'.[/red]")


@app.command()
def edit() -> None:
    """Open the alias file in the default editor."""
    editor = os.environ.get("EDITOR", "nano")
    subprocess.call([editor, str(config.alias_file)])


@app.command()
def remove() -> None:
    """Interactively remove aliases."""
    if not config.alias_file.exists():
        console.print("[yellow]No aliases found.[/yellow]")
        return

    content = config.alias_file.read_text()
    groups = parse_aliases(content)

    # Flatten for selection
    choices = []
    alias_map = {}
    for g_name, aliases in groups.items():
        for alias in aliases:
            choice_str = f"[{g_name}] {alias.name} -> {alias.command}"
            choices.append(choice_str)
            alias_map[choice_str] = (g_name, alias)

    if not choices:
        console.print("[yellow]No aliases to remove.[/yellow]")
        return

    selected = questionary.checkbox(
        "Select aliases to remove:",
        choices=choices,
    ).ask()

    if not selected:
        return

    # Show confirmation table
    table = Table(title="Aliases to Remove")
    table.add_column("Group", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Command")

    to_remove = []
    for s in selected:
        g_name, alias = alias_map[s]
        to_remove.append((g_name, alias))
        table.add_row(g_name, alias.name, alias.command)

    console.print(table)

    if not questionary.confirm(
        f"Are you sure you want to remove these {len(to_remove)} aliases?",
    ).ask():
        console.print("[yellow]Operation cancelled.[/yellow]")
        return

    # Remove
    for g_name, alias in to_remove:
        if alias in groups[g_name]:
            groups[g_name].remove(alias)

    new_content = serialize_aliases(groups)
    config.alias_file.write_text(new_content)
    console.print(f"[green]Removed {len(to_remove)} aliases.[/green]")


if __name__ == "__main__":
    app()

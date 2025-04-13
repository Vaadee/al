"""Python script to handle aliases."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

# alias file path
alias_file_path = r"/Users/vaadeendra/petp/al/aliases.sh"

console = Console()

app = typer.Typer()
view_commands = typer.Typer()
app.add_typer(view_commands, name="view", help="View the aliases.")
edit_commands = typer.Typer()
app.add_typer(edit_commands, name="edit", help="Edit the aliases.")


def convert_script_to_json(alias_file_path: str) -> str:
    """Convert the script to JSON."""
    # Define a regular expression pattern to match the sections
    section_pattern = r"\#\[\s*([^\]]+)\s*\]((?:\n[^\#]*)+)"
    alias_pattern = r'alias\s+([\w.]+)\s*=\s*"([^"]+)"'

    try:
        # Read the script file
        with Path(alias_file_path).open(encoding="utf-8") as file:
            script_content = file.read()

        # Initialize an empty dictionary to store the JSON data
        output_data = {}

        # Find all sections in the script
        sections = re.findall(section_pattern, script_content)

        # Iterate through the sections
        for section in sections:
            group_name = section[0].strip()
            alias_commands = section[1]

            # Find all alias commands in the section
            aliases = re.findall(alias_pattern, alias_commands)

            # Create a list of dictionaries for the aliases and commands
            aliases_list = [
                {"alias": alias, "command": command} for alias, command in aliases
            ]

            # Add aliases list to output dictionary with group name as key
            output_data[group_name] = aliases_list

        # Convert the output data to JSON
        output_json = json.dumps(output_data, indent=2)

        return json.loads(output_json)

    except FileNotFoundError:
        return "File not found."


def recreate_script_from_json(data: dict, alias_file_path: str) -> str:
    """Recreate the script from JSON."""
    try:
        # sort the data by key then by alias
        data = dict(sorted(data.items(), key=lambda x: x[0]))
        for key in data:
            data[key] = sorted(data[key], key=lambda x: x["alias"])

        # Initialize a string to hold the script content
        script_content = ""

        # Iterate through the data to construct the script
        for section, aliases in data.items():
            # Add section header
            script_content += f"#[{section}]\n"

            # Add each alias command
            for alias in aliases:
                script_content += f'alias {alias["alias"]}="{alias["command"]}"\n'

            # Add a newline for separation between sections
            script_content += "\n"

        # Write the script content to the file
        with Path(alias_file_path).open("w", encoding="utf-8") as file:
            file.write(script_content)

    except json.JSONDecodeError:
        return "Invalid JSON format."
    except OSError as e:
        return f"File operation error: {e!s}"
    except KeyError as e:
        return f"Missing key error: {e!s}"
    except TypeError as e:
        return f"Type error: {e!s}"
    else:
        # source the file
        return (
            f"Script successfully updated at {alias_file_path}\n"
            "Run `source ~/.bashrc` to update the aliases."
        )


@view_commands.command(name="list")
def list_commands(
    group: Annotated[
        str | None,
        typer.Option("-g", "--group", help="Name of the group to list commands from"),
    ] = "all",
) -> None:
    """List all commands or commands filtered by group."""
    output_json = convert_script_to_json(alias_file_path)
    if group == "all":
        # print the entire json as table with colors
        table = Table(title="Aliases")
        table.add_column("Group", style="cyan")
        table.add_column("Alias", style="magenta")
        table.add_column("Command", style="green")
        for group_name, alias_list in output_json.items():
            for alias in alias_list:
                table.add_row(group_name, alias["alias"], alias["command"])

        console.print(table)
    else:
        # print the json filtered by group
        table = Table(title="Aliases")
        table.add_column("Alias", style="magenta")
        table.add_column("Command", style="green")
        for alias in output_json[group]:
            table.add_row(alias["alias"], alias["command"])

        console.print(table)


@edit_commands.command(name="add")
def add_command(
    alias: Annotated[
        str,
        typer.Option("-a", "--alias", help="Alias to add"),
    ],
    command: Annotated[
        str,
        typer.Option("-c", "--command", help="Command to add"),
    ],
    group: Annotated[
        str,
        typer.Option("-g", "--group", help="Name of the group to add command to"),
    ] = "main",
) -> None:
    """Add a command to the aliases."""
    output_json = convert_script_to_json(alias_file_path)

    # check if the group and alias already exists
    for alias_dict in output_json.get(group, []):
        if alias_dict["alias"] == alias:
            console.print("Alias already exists")
            sys.exit(1)

    if group not in output_json:
        # add the group to the json
        output_json[group] = []

    # add the alias to the json
    output_json[group].append({"alias": alias, "command": command})
    output = recreate_script_from_json(output_json, alias_file_path)
    console.print(output)


@edit_commands.command(name="remove")
def remove_command(
    alias: Annotated[
        str,
        typer.Option("-a", "--alias", help="Alias to remove"),
    ],
    group: Annotated[
        str,
        typer.Option("-g", "--group", help="Name of the group to remove command from"),
    ] = "main",
) -> None:
    """Remove a command from the aliases."""
    output_json = convert_script_to_json(alias_file_path)

    # check if the group and alias already exists
    for alias_dict in output_json.get(group, []):
        if alias_dict["alias"] == alias:
            output_json[group].remove(alias_dict)
            output = recreate_script_from_json(output_json, alias_file_path)
            console.print(output)
            sys.exit(0)

    console.print("Alias not found")
    sys.exit(1)


@edit_commands.command(name="update")
def update_command(
    alias: Annotated[
        str,
        typer.Option("-a", "--alias", help="Alias to update"),
    ],
    command: Annotated[
        str,
        typer.Option("-c", "--command", help="Command to update"),
    ],
    group: Annotated[
        str,
        typer.Option("-g", "--group", help="Name of the group to update command from"),
    ] = "main",
) -> None:
    """Update a command from the aliases."""
    output_json = convert_script_to_json(alias_file_path)

    # check if the group and alias already exists
    for alias_dict in output_json.get(group, []):
        if alias_dict["alias"] == alias:
            alias_dict["command"] = command
            output = recreate_script_from_json(output_json, alias_file_path)
            console.print(output)
            sys.exit(0)

    console.print("Alias not found")
    sys.exit(1)


@view_commands.command(name="search")
def search_command(
    alias: Annotated[
        str,
        typer.Option("-a", "--alias", help="Alias to search"),
    ],
    group: Annotated[
        str,
        typer.Option("-g", "--group", help="Name of the group to search command from"),
    ] = "all",
) -> None:
    """Search a command from the aliases."""
    output_json = convert_script_to_json(alias_file_path)

    # check if the alias already exists and if the group is all search in all groups
    for group_name, alias_list in output_json.items():
        if group in {"all", group_name}:
            for alias_dict in alias_list:
                if alias_dict["alias"] == alias:
                    table = Table()
                    table.add_column("Group", style="cyan")
                    table.add_column("Alias", style="magenta")
                    table.add_column("Command", style="green")
                    table.add_row(
                        group_name,
                        alias_dict["alias"],
                        alias_dict["command"],
                    )
                    console.print(table)
                    sys.exit(0)

    console.print("Alias not found")
    sys.exit(1)


@edit_commands.command(name="script")
def script_command() -> None:
    """Edit  the aliases script using nano."""
    # Ensure the command uses a trusted executable and file path
    # Validate that alias_file_path is a trusted file path
    if Path(alias_file_path).is_file():
        subprocess.run(["/usr/bin/nano", alias_file_path], check=True, text=True)
    else:
        console.print("Error: Invalid or untrusted file path.", style="bold red")
    console.print(
        "Script updated successfully. Run `source ~/.bashrc` to update the aliases.",
    )

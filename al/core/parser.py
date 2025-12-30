"""Parser for alias files."""

import re
from dataclasses import dataclass


@dataclass
class Alias:
    """Represents a single alias."""

    name: str
    command: str
    group: str = "main"


def parse_aliases(content: str) -> dict[str, list[Alias]]:
    """
    Parse alias file content into groups.

    Format:
    #[group_name]
    alias name="command"

    Args:
        content (str): The raw content of the alias file.

    Returns:
        dict[str, list[Alias]]: A dictionary mapping group names to lists of Alias
            objects.

    """
    groups: dict[str, list[Alias]] = {}
    current_group = "main"

    # Ensure main group exists
    groups[current_group] = []

    lines = content.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # Check for group header
        group_match = re.match(r"^#\[(.*)\]$", line)
        if group_match:
            current_group = group_match.group(1)
            if current_group not in groups:
                groups[current_group] = []
            continue

        # Check for alias definition
        # Matches: alias name="command" or alias name='command'
        # We need to be careful with quotes in the command
        alias_match = re.match(r"^alias\s+([\w\.-]+)=[\"'](.*)[\"']$", line)
        if alias_match:
            name = alias_match.group(1)
            command = alias_match.group(2)
            groups[current_group].append(
                Alias(name=name, command=command, group=current_group),
            )
            continue

    return groups


def serialize_aliases(groups: dict[str, list[Alias]]) -> str:
    """
    Serialize groups back to string format.

    Args:
        groups (dict[str, list[Alias]]): The groups of aliases to serialize.

    Returns:
        str: The serialized content string.

    """
    lines = []

    # Sort groups, keeping main first if possible or just alphabetical
    sorted_groups = sorted(groups.keys())

    for group in sorted_groups:
        aliases = groups[group]
        if not aliases:
            continue

        lines.append(f"#[{group}]")
        for alias in aliases:
            # Escape double quotes in command if we use double quotes wrapper
            # For simplicity, we'll use double quotes and escape existing ones
            safe_command = alias.command.replace('"', '\\"')
            lines.append(f'alias {alias.name}="{safe_command}"')
        lines.append("")  # Empty line between groups

    return "\n".join(lines)

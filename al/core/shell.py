"""Shell integration utilities."""

from .config import config


def ensure_shell_source() -> tuple[bool, str]:
    """Ensure the alias file is sourced in the shell rc file.

    Returns:
        tuple[bool, str]: A tuple containing success status and a message.

    """
    rc_file = config.shell_rc
    if not rc_file or not rc_file.exists():
        return False, "Could not detect shell rc file or it does not exist."

    alias_path = config.alias_file
    source_cmd = f'source "{alias_path}"'

    # Check if already sourced
    content = rc_file.read_text()
    if source_cmd in content:
        return True, "Already sourced."

    # Append to rc file
    with rc_file.open("a") as f:
        f.write(f"\n# al CLI aliases\n{source_cmd}\n")

    return True, f"Added source command to {rc_file}"

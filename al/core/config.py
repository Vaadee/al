"""Configuration management for al."""

import json
import os
from pathlib import Path


class Config:
    """Configuration management for al."""

    APP_NAME = "al"

    def __init__(self) -> None:
        """Initialize configuration paths."""
        self.home = Path.home()
        self.config_dir = self.home / ".config" / self.APP_NAME
        self.alias_file = self.config_dir / "aliases"
        self.sync_file = self.config_dir / "sync.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.alias_file.exists():
            self.alias_file.touch()

    def load_sync_config(self) -> dict:
        """Load synchronization configuration from JSON file.

        Returns:
            dict: The configuration data.

        """
        if self.sync_file.exists():
            return json.loads(self.sync_file.read_text())
        return {}

    def save_sync_config(self, data: dict) -> None:
        """Save synchronization configuration to JSON file.

        Args:
            data (dict): The configuration data to save.

        """
        self.sync_file.write_text(json.dumps(data, indent=2))

    @property
    def shell_rc(self) -> Path | None:
        """Get the path to the shell configuration file.

        Returns:
            Path | None: Path to .zshrc or .bashrc, or None if not detected.

        """
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            return self.home / ".zshrc"
        if "bash" in shell:
            return self.home / ".bashrc"
        return None


config = Config()

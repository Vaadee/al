"""Tests for reserved alias validation."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from al.main import app

runner = CliRunner()


def test_add_reserved_alias(tmp_path: Path) -> None:
    """Test adding an alias with a reserved name."""
    config_dir = tmp_path / ".config" / "al"
    config_dir.mkdir(parents=True)
    alias_file = config_dir / "aliases"
    alias_file.touch()

    with (
        patch("al.core.config.config.alias_file", alias_file),
        # Mock questionary to simulate user input
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("al.main.is_initialized", return_value=True),
    ):
        mock_select.return_value.ask.return_value = "main"
        # Try to add 'al' as an alias
        mock_text.return_value.ask.side_effect = ["al"]

        result = runner.invoke(app, ["add"])
        assert result.exit_code == 0
        assert "Alias name 'al' is reserved." in result.stdout

        # Verify it wasn't added
        content = alias_file.read_text()
        assert "alias al=" not in content

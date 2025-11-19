"""Tests for the CLI commands."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest
from typer.testing import CliRunner

from al.main import app

runner = CliRunner()


@pytest.fixture
def mock_config(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a mock configuration directory and alias file."""
    config_dir = tmp_path / ".config" / "al"
    config_dir.mkdir(parents=True)
    alias_file = config_dir / "aliases"
    alias_file.touch()

    with patch("al.core.config.config.alias_file", alias_file):
        yield alias_file


def test_init(tmp_path: Path) -> None:
    """Test the init command."""
    with patch(
        "al.core.config.Config.shell_rc",
        new_callable=PropertyMock,
    ) as mock_prop:
        mock_prop.return_value = tmp_path / ".zshrc"
        (tmp_path / ".zshrc").touch()
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Added source command" in result.stdout


def test_add_interactive(mock_config: Path) -> None:
    """Test adding an alias interactively."""
    # Mock questionary to simulate user input
    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
    ):
        mock_select.return_value.ask.return_value = "main"
        mock_text.return_value.ask.side_effect = ["foo", "echo bar"]

        result = runner.invoke(app, ["add"])
        assert result.exit_code == 0
        assert "Alias 'foo' added" in result.stdout

        content = mock_config.read_text()
        assert 'alias foo="echo bar"' in content


def test_view(mock_config: Path) -> None:
    """Test viewing aliases."""
    mock_config.write_text('#[main]\nalias foo="echo bar"')
    result = runner.invoke(app, ["view"])
    assert result.exit_code == 0
    assert "foo" in result.stdout
    assert "echo bar" in result.stdout


def test_search(mock_config: Path) -> None:
    """Test searching aliases."""
    mock_config.write_text('#[main]\nalias foo="echo bar"')
    result = runner.invoke(app, ["search", "foo"])
    assert result.exit_code == 0
    assert "foo" in result.stdout


def test_remove(mock_config: Path) -> None:
    """Test removing an alias."""
    mock_config.write_text('#[main]\nalias foo="echo bar"')

    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "[main] foo -> echo bar"

        result = runner.invoke(app, ["remove"])
        assert result.exit_code == 0
        assert "Alias removed" in result.stdout

        content = mock_config.read_text()
        assert "foo" not in content

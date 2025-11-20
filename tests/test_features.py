"""Tests for new features: init check and enhanced remove."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from al.main import app

runner = CliRunner()


@pytest.fixture
def mock_config(tmp_path: Path):
    """Create a mock configuration directory and alias file."""
    config_dir = tmp_path / ".config" / "al"
    config_dir.mkdir(parents=True)
    alias_file = config_dir / "aliases"
    alias_file.touch()

    with patch("al.core.config.config.alias_file", alias_file):
        yield alias_file


def test_init_check_fail(tmp_path: Path):
    """Test that commands fail if not initialized."""
    # Mock is_initialized to return False
    # We must patch al.main.is_initialized because it's imported into main
    with patch("al.main.is_initialized", return_value=False):
        result = runner.invoke(app, ["add"])
        assert result.exit_code == 1
        assert "al is not initialized" in result.stdout


def test_init_check_pass(tmp_path: Path):
    """Test that commands pass if initialized."""
    # Mock is_initialized to return True
    with patch("al.main.is_initialized", return_value=True):
        # We need to mock other things for 'add' to work, so let's use 'view' which is simpler
        # But view also needs config file
        config_dir = tmp_path / ".config" / "al"
        config_dir.mkdir(parents=True)
        alias_file = config_dir / "aliases"
        alias_file.touch()

        with patch("al.core.config.config.alias_file", alias_file):
            result = runner.invoke(app, ["view"])
            assert result.exit_code == 0


def test_enhanced_remove(mock_config: Path):
    """Test enhanced remove command."""
    mock_config.write_text('#[main]\nalias foo="echo bar"\nalias baz="echo qux"')

    with patch("al.main.is_initialized", return_value=True):
        with (
            patch("questionary.checkbox") as mock_checkbox,
            patch("questionary.confirm") as mock_confirm,
        ):
            # Select both aliases
            mock_checkbox.return_value.ask.return_value = [
                "[main] foo -> echo bar",
                "[main] baz -> echo qux",
            ]
            # Confirm removal
            mock_confirm.return_value.ask.return_value = True

            result = runner.invoke(app, ["remove"])
            assert result.exit_code == 0
            assert "Removed 2 aliases" in result.stdout

            content = mock_config.read_text()
            assert "foo" not in content
            assert "baz" not in content


def test_enhanced_remove_cancel(mock_config: Path):
    """Test cancelling enhanced remove."""
    mock_config.write_text('#[main]\nalias foo="echo bar"')

    with patch("al.main.is_initialized", return_value=True):
        with (
            patch("questionary.checkbox") as mock_checkbox,
            patch("questionary.confirm") as mock_confirm,
        ):
            mock_checkbox.return_value.ask.return_value = ["[main] foo -> echo bar"]
            # Cancel removal
            mock_confirm.return_value.ask.return_value = False

            result = runner.invoke(app, ["remove"])
            assert result.exit_code == 0
            assert "Operation cancelled" in result.stdout

            content = mock_config.read_text()
            assert "foo" in content

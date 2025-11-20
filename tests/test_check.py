"""Tests for the check command."""

from pathlib import Path
from unittest.mock import PropertyMock, patch

from typer.testing import CliRunner

from al.main import app

runner = CliRunner()


def test_check_healthy(tmp_path: Path) -> None:
    """Test check command when everything is healthy."""
    config_dir = tmp_path / ".config" / "al"
    config_dir.mkdir(parents=True)
    alias_file = config_dir / "aliases"
    alias_file.touch()

    with patch("al.core.config.config.alias_file", alias_file):
        with patch("al.core.config.config.config_dir", config_dir):
            with patch(
                "al.core.config.Config.shell_rc",
                new_callable=PropertyMock,
            ) as mock_rc:
                rc_file = tmp_path / ".zshrc"
                rc_file.touch()
                mock_rc.return_value = rc_file

                with patch("al.main.is_initialized", return_value=True):
                    result = runner.invoke(app, ["check"])
                    assert result.exit_code == 0
                    assert "System Check" in result.stdout
                    assert "Config Directory" in result.stdout
                    assert "✅" in result.stdout
                    assert "❌" not in result.stdout


def test_check_unhealthy(tmp_path: Path) -> None:
    """Test check command when things are missing."""
    # Don't create files

    # We need to mock config paths to point to tmp_path so they definitely don't exist
    # But config object is already instantiated in main.py
    # We can patch the properties or attributes

    with patch("al.core.config.config.alias_file", tmp_path / "missing_aliases"):
        with patch("al.core.config.config.config_dir", tmp_path / "missing_dir"):
            with patch(
                "al.core.config.Config.shell_rc",
                new_callable=PropertyMock,
            ) as mock_rc:
                mock_rc.return_value = None

                with patch("al.main.is_initialized", return_value=False):
                    result = runner.invoke(app, ["check"])
                    assert result.exit_code == 0
                    assert "System Check" in result.stdout
                    assert "❌" in result.stdout

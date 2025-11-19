"""Tests for configuration management."""

from pathlib import Path
from unittest.mock import patch

from al.core.config import Config


def test_config_paths() -> None:
    """Test that configuration paths are correctly resolved."""
    with patch("pathlib.Path.home") as mock_home:
        mock_home.return_value = Path("/tmp/mock_home")

        config = Config()
        assert config.config_dir == Path("/tmp/mock_home/.config/al")
        assert config.alias_file == Path("/tmp/mock_home/.config/al/aliases")


def test_shell_detection_zsh() -> None:
    """Test detection of zsh shell."""
    with patch("os.environ.get") as mock_env:
        mock_env.return_value = "/bin/zsh"
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/mock_home")
            config = Config()
            assert config.shell_rc == Path("/tmp/mock_home/.zshrc")


def test_shell_detection_bash() -> None:
    """Test detection of bash shell."""
    with patch("os.environ.get") as mock_env:
        mock_env.return_value = "/bin/bash"
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/mock_home")
            config = Config()
            assert config.shell_rc == Path("/tmp/mock_home/.bashrc")

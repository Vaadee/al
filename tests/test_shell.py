"""Tests for shell integration."""

from unittest.mock import MagicMock, PropertyMock, patch

from al.core.shell import ensure_shell_source


def test_ensure_shell_source_no_rc() -> None:
    """Test behavior when no shell rc file is detected."""
    with patch(
        "al.core.config.Config.shell_rc",
        new_callable=PropertyMock,
    ) as mock_prop:
        mock_prop.return_value = None
        success, msg = ensure_shell_source()
        assert success is False
        assert "Could not detect" in msg


def test_ensure_shell_source_already_sourced() -> None:
    """Test behavior when alias file is already sourced."""
    mock_rc = MagicMock()
    mock_rc.exists.return_value = True
    mock_rc.read_text.return_value = 'source "/path/to/aliases"'

    with patch(
        "al.core.config.Config.shell_rc",
        new_callable=PropertyMock,
    ) as mock_prop:
        mock_prop.return_value = mock_rc
        with patch("al.core.config.config.alias_file") as mock_alias:
            mock_alias.__str__.return_value = "/path/to/aliases"
            success, msg = ensure_shell_source()
            assert success is True
            assert "Already sourced" in msg


def test_ensure_shell_source_append() -> None:
    """Test appending source command to shell rc file."""
    mock_rc = MagicMock()
    mock_rc.exists.return_value = True
    mock_rc.read_text.return_value = "some other content"

    with patch(
        "al.core.config.Config.shell_rc",
        new_callable=PropertyMock,
    ) as mock_prop:
        mock_prop.return_value = mock_rc
        with patch("al.core.config.config.alias_file") as mock_alias:
            mock_alias.__str__.return_value = "/path/to/aliases"
            success, msg = ensure_shell_source()
            assert success is True
            assert "Added source command" in msg
            mock_rc.open.assert_called_once_with("a")

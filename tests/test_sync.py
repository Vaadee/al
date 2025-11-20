"""Tests for Gist synchronization."""

from unittest.mock import patch

from al.core.sync import GistSync


def test_push_new() -> None:
    """Test pushing new aliases to Gist."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "new_id"}

        sync = GistSync("token")
        success, result = sync.push("content")

        assert success is True
        assert result == "new_id"
        mock_post.assert_called_once()


def test_push_existing() -> None:
    """Test updating existing aliases in Gist."""
    with patch("requests.patch") as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"id": "existing_id"}

        sync = GistSync("token")
        success, result = sync.push("content", "existing_id")

        assert success is True
        assert result == "existing_id"
        mock_patch.assert_called_once()


def test_pull_success() -> None:
    """Test pulling aliases from Gist successfully."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "files": {"aliases.sh": {"content": "alias foo='bar'"}},
        }

        sync = GistSync("token")
        success, result = sync.pull("some_id")

        assert success is True
        assert result == "alias foo='bar'"


def test_pull_fail() -> None:
    """Test pulling aliases from Gist failure."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        sync = GistSync("token")
        success, _result = sync.pull("bad_id")

        assert success is False

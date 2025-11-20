"""GitHub Gist synchronization module."""

import requests

GITHUB_API_URL = "https://api.github.com"


class GistSync:
    """Handles synchronization with GitHub Gists."""

    def __init__(self, token: str) -> None:
        """Initialize GistSync with a GitHub token.

        Args:
            token (str): GitHub Personal Access Token.

        """
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def push(self, content: str, gist_id: str | None = None) -> tuple[bool, str]:
        """Push content to a Gist.

        If gist_id is provided, update it. Otherwise create new.

        Args:
            content (str): The content to push.
            gist_id (str | None): Optional ID of an existing Gist to update.

        Returns:
            tuple[bool, str]: A tuple containing success status and the Gist ID
                (or error message).

        """
        data = {
            "description": "al-cli aliases backup",
            "public": False,
            "files": {"aliases.sh": {"content": content}},
        }

        try:
            if gist_id:
                # Update existing
                resp = requests.patch(
                    f"{GITHUB_API_URL}/gists/{gist_id}",
                    headers=self.headers,
                    json=data,
                    timeout=10,
                )
            else:
                # Create new
                resp = requests.post(
                    f"{GITHUB_API_URL}/gists",
                    headers=self.headers,
                    json=data,
                    timeout=10,
                )

            if resp.status_code in (200, 201):
                return True, resp.json()["id"]
            return False, f"GitHub API Error: {resp.status_code} - {resp.text}"
        except Exception as e:
            return False, str(e)

    def pull(self, gist_id: str) -> tuple[bool, str]:
        """Pull content from a Gist.

        Args:
            gist_id (str): The ID of the Gist to pull from.

        Returns:
            tuple[bool, str]: A tuple containing success status and the content
                (or error message).

        """
        try:
            resp = requests.get(
                f"{GITHUB_API_URL}/gists/{gist_id}",
                headers=self.headers,
                timeout=10,
            )
            if resp.status_code == 200:
                files = resp.json().get("files", {})
                if "aliases.sh" in files:
                    return True, files["aliases.sh"]["content"]
                return False, "Gist does not contain 'aliases.sh'"
            return False, f"GitHub API Error: {resp.status_code} - {resp.text}"
        except Exception as e:
            return False, str(e)

"""
GitHub API client (preloaded) — the OPTIONAL pull-request input path.

Only used when a GITHUB_TOKEN is set and the reviewer chooses the "GitHub PR"
input in the console; the default input is local code (paste / upload / sample).
"""

import base64
import logging
from typing import Any, Dict, List

import requests

from config import config

logger = logging.getLogger("github_client")


class GitHubClient:
    """Fetches a PR's changed Python files from the GitHub REST API."""

    def __init__(self):
        self.api_url = config.github_api_url
        self.headers = {"Accept": "application/vnd.github+json"}
        if config.github_token:
            self.headers["Authorization"] = f"token {config.github_token}"

    def get_pr_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """Return the PR's changed Python files with their content."""
        url = f"{self.api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        files: List[Dict[str, Any]] = []
        for entry in response.json():
            filename = entry.get("filename", "")
            if filename.endswith(".py"):
                files.append({
                    "filename": filename,
                    "content": self._get_file_content(entry.get("contents_url", "")),
                })
        return files

    def _get_file_content(self, contents_url: str) -> str:
        """Fetch and base64-decode a single file's content."""
        if not contents_url:
            return ""
        try:
            response = requests.get(contents_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception as error:
            logger.warning(f"Could not fetch file content: {error}")
        return ""

"""
Ingest node.

Implement ingest_node(state): populate state["files"] — pass local files through, or fetch a GitHub
PR's files via GitHubClient when that is the source. See the problem description for the contract.
"""
from state import ReviewState
from config import config
from services.github_client import GitHubClient


def ingest_node(state: ReviewState) -> dict:
    source = state.get("source", "local")
    files = state.get("files", [])

    if source == "local":
        return {"files": files}

    if source == "github":
        if files:
            return {"files": files}

        try:
            client = GitHubClient()
            fetched_files = client.get_pr_files(state.get("pr_details", {}))

            return {"files": fetched_files}

        except Exception as exc:
            return {
                "files": [],
                "errors": [
                    {
                        "node": "ingest",
                        "error": str(exc),
                    }
                ],
            }

    return {
        "files": files,
        "errors": [
            {
                "node": "ingest",
                "error": f"Unsupported source: {source}",
            }
        ],
    }

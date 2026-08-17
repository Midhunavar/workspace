"""
Security node.

Implement security_node(state): run SecurityAgent on state["files"] and return
{"security_results": ...}; on failure return [] plus an errors entry. See the problem description
for the contract.
"""
from state import ReviewState
from agents.security_agent import SecurityAgent


def security_node(state: ReviewState) -> dict:
    try:
        agent = SecurityAgent()

        return {
            "security_results": agent.analyze(
                state.get("files", [])
            )
        }

    except Exception as exc:
        return {
            "security_results": [],
            "errors": [
                {
                    "node": "security",
                    "error": str(exc),
                }
            ],
        }

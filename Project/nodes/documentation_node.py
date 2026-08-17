"""
Documentation node.

Implement documentation_node(state): run DocumentationAgent on state["files"] and return
{"documentation_results": ...}; on failure return [] plus an errors entry. See the problem
description for the contract.
"""
from state import ReviewState
from agents.documentation_agent import DocumentationAgent


def documentation_node(state: ReviewState) -> dict:
    try:
        agent = DocumentationAgent()

        return {
            "documentation_results": agent.analyze(
                state.get("files", [])
            )
        }

    except Exception as exc:
        return {
            "documentation_results": [],
            "errors": [
                {
                    "node": "documentation",
                    "error": str(exc),
                }
            ],
        }

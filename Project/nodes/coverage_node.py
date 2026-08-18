"""
Coverage node.

Implement coverage_node(state): run CoverageAgent on state["files"] and return
{"coverage_results": ...}; on failure return [] plus an errors entry. See the problem description
for the contract.
"""
from state import ReviewState
from agents.coverage_agent import CoverageAgent
from config import config


def coverage_node(state: ReviewState) -> dict:
    try:
        agent = CoverageAgent(config)

        return {
            "coverage_results": agent.analyze(
                state.get("files", [])
            )
        }

    except Exception as exc:
        return {
            "coverage_results": [],
            "errors": [
                {
                    "node": "coverage",
                    "error": str(exc),
                }
            ],
        }

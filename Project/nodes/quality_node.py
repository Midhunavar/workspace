"""
Quality node.

Implement quality_node(state): run QualityAgent on state["files"] and return
{"quality_results": ...}; on failure return [] plus an errors entry. See the problem description
for the contract.
"""
from state import ReviewState
from agents.quality_agent import QualityAgent
from config import config


def quality_node(state: ReviewState) -> dict:
    try:
        agent = QualityAgent(config)

        return {
            "quality_results": agent.analyze(
                state.get("files", [])
            )
        }

    except Exception as exc:
        return {
            "quality_results": [],
            "errors": [
                {
                    "node": "quality",
                    "error": str(exc),
                }
            ],
        }

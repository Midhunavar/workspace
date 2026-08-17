"""
AI review node.

Implement ai_review_node(state): run AIReviewAgent on state["files"] and return
{"ai_reviews": ...}; on failure return [] plus an errors entry. See the problem description for the
contract.
"""
from state import ReviewState
from agents.ai_review_agent import AIReviewAgent


def ai_review_node(state: ReviewState) -> dict:
    try:
        agent = AIReviewAgent()

        return {
            "ai_reviews": agent.analyze(
                state.get("files", [])
            )
        }

    except Exception as exc:
        return {
            "ai_reviews": [],
            "errors": [
                {
                    "node": "ai_review",
                    "error": str(exc),
                }
            ],
        }

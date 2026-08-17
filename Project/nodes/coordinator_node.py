"""
Coordinator node.

Implement coordinator_node(state): average each analysis dimension across files into
coordination_summary. See the problem description for the exact summary keys and the per-file source
field each average reads.
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

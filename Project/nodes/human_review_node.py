"""
Human review node (HITL).

Implement human_review_node(state): call interrupt(payload) to pause the graph, and store the
resumed Command(resume=...) action in human_decision. See the problem description for the interrupt
payload keys.
"""
from langgraph.types import interrupt

from state import ReviewState


def human_review_node(state: ReviewState) -> dict:
    payload = {
        "review_id": state.get("review_id"),
        "decision": state.get("decision"),
        "decision_metrics": state.get(
            "decision_metrics",
            {},
        ),
        "critical_issues": state.get(
            "critical_issues",
            [],
        ),
        "message": (
            "Code review requires human approval. "
            "Approve or reject this review."
        ),
    }

    human_decision = interrupt(payload)

    return {
        "human_decision": human_decision
    }

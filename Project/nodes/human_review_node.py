"""
Human review node (HITL).

Implement human_review_node(state): call interrupt(payload) to pause the graph, and store the
resumed Command(resume=...) action in human_decision. See the problem description for the interrupt
payload keys.
"""
from langgraph.types import interrupt

from state import ReviewState


def human_review_node(state: ReviewState) -> dict:
    metrics = state.get(
        "decision_metrics",
        {},
    )

    interrupt_payload = {
        "review_id": state.get(
            "review_id"
        ),
        "decision": state.get(
            "decision"
        ),
        "metrics": metrics,
        "high_severity_issues": metrics.get(
            "high_severity_issues",
            0,
        ),
        "question": (
            "The code review requires human intervention. "
            "Do you approve or reject this review?"
        ),
    }

    human_decision = interrupt(
        interrupt_payload
    )

    return {"human_decision": human_decision}

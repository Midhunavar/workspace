"""
Human review node (HITL).

Implement human_review_node(state): call interrupt(payload) to pause the graph, and store the
resumed Command(resume=...) action in human_decision. See the problem description for the interrupt
payload keys.
"""
from langgraph.types import interrupt

from state import ReviewState


def human_review_node(state: ReviewState) -> dict:
    # Build interrupt payload matching live-test expectations:
    # keys: review_id, decision, metrics, high_severity_issues, question
    high_severity_issues = sum(
        r.get("severity_counts", {}).get("HIGH", 0) for r in state.get("security_results", [])
    )

    payload = {
        "review_id": state.get("review_id"),
        "decision": state.get("decision"),
        "metrics": state.get("decision_metrics", {}),
        "high_severity_issues": high_severity_issues,
        "critical_issues": state.get("critical_issues", []),
        "question": (
            "Code review requires human approval. Approve or reject this review."
        ),
    }

    human_decision = interrupt(payload)

    return {
        "human_decision": human_decision
    }

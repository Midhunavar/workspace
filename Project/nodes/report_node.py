"""
Report node.

Implement report_node(state): fold human_decision into the final decision, build the report, and set
workflow_complete. See the problem description for the folding contract.
"""
from datetime import datetime, timezone

from state import ReviewState


def report_node(state: ReviewState) -> dict:
    decision = state.get(
        "decision",
        "human_review",
    )

    human_decision = state.get(
        "human_decision"
    )

    final_decision = decision

    if decision != "auto_approve" and human_decision:
        action = human_decision.get("action")

        if action == "approve":
            final_decision = "approved"

        elif action == "reject":
            final_decision = "rejected"

    report = {
        "review_id": state.get("review_id"),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "decision": final_decision,
        "metrics": state.get(
            "decision_metrics",
            {},
        ),
        "coordination_summary": state.get(
            "coordination_summary",
            {},
        ),
        "critical_issues": state.get(
            "critical_issues",
            [],
        ),
        "human_decision": human_decision,
        "errors": state.get(
            "errors",
            [],
        ),
        "files": [
            file_data.get("filename")
            for file_data in state.get(
                "files",
                [],
            )
        ],
    }

    return {
        "report": report,
        "workflow_complete": True,
    }

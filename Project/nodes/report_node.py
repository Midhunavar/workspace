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

    # support multiple shapes for `human_decision` used in tests and runtime:
    # - a plain string: "approve" / "reject"
    # - a dict with an "action" key
    # - a dict with a nested "resume": {"action": ...}
    action = None
    if human_decision:
        if isinstance(human_decision, str):
            action = human_decision
        elif isinstance(human_decision, dict):
            action = human_decision.get("action") or (human_decision.get("resume") or {}).get("action")
        else:
            # best-effort: try attribute access (e.g. Command objects)
            action = getattr(human_decision, "action", None)
            if action is None:
                resume = getattr(human_decision, "resume", None)
                if isinstance(resume, dict):
                    action = resume.get("action")
                elif isinstance(resume, str):
                    action = resume

    if decision != "auto_approve" and action:
        if action == "approve":
            final_decision = "approved_by_reviewer"
        elif action == "reject":
            final_decision = "rejected_by_reviewer"

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

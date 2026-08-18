"""
Report node.

Implement report_node(state): fold human_decision into the final decision, build the report, and set
workflow_complete. See the problem description for the folding contract.
"""
from state import ReviewState


def _priority_for_decision(decision: str) -> str:
    if decision == "critical_escalation":
        return "critical"

    if decision == "human_review":
        return "high"

    if decision == "auto_approve":
        return "low"

    if decision == "approved_by_reviewer":
        return "high"

    if decision == "rejected_by_reviewer":
        return "critical"

    return "medium"


def report_node(state: ReviewState) -> dict:
    pipeline_decision = state.get(
        "decision",
        "auto_approve",
    )

    human_decision = state.get(
        "human_decision",
        "",
    )

    # Human decision overrides pipeline decision
    # only when HITL actually occurred.
    if human_decision == "approve":
        final_decision = "approved_by_reviewer"

    elif human_decision == "reject":
        final_decision = "rejected_by_reviewer"

    else:
        final_decision = pipeline_decision

    metrics = state.get(
        "decision_metrics",
        {},
    )

    key_findings = []
    action_items = []

    if metrics.get("high_severity_issues", 0) > 0:
        key_findings.append(
            "High-severity security issues were detected."
        )
        action_items.append(
            "Resolve all high-severity security issues."
        )

    if metrics.get("security_score", 0) < 8.0:
        key_findings.append(
            "Security score is below the required threshold."
        )
        action_items.append(
            "Address security concerns before approval."
        )

    if metrics.get("pylint_score", 0) < 7.0:
        key_findings.append(
            "Code quality score is below the required threshold."
        )
        action_items.append(
            "Resolve code-quality issues identified by PyLint."
        )

    if metrics.get("coverage", 0) < 80.0:
        key_findings.append(
            "Test coverage is below the required threshold."
        )
        action_items.append(
            "Add tests to improve coverage."
        )

    if metrics.get("ai_score", 0) < 0.8:
        key_findings.append(
            "Holistic AI review score is below the threshold."
        )
        action_items.append(
            "Review the AI findings and improve the implementation."
        )

    if metrics.get(
        "documentation_coverage",
        0,
    ) < 70.0:
        key_findings.append(
            "Documentation coverage is below the threshold."
        )
        action_items.append(
            "Add missing documentation and docstrings."
        )

    report = {
        "review_id": state.get(
            "review_id"
        ),
        "priority": _priority_for_decision(
            final_decision
        ),
        "metrics": metrics,
        "key_findings": key_findings,
        "action_items": action_items,
        "decision": final_decision,
    }

    return {
        "report": report,
        "workflow_complete": True,
    }

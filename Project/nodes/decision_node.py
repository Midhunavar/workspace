"""
Decision node.

Implement decision_node(state): apply the quality gates to the coordination_summary averages and the
high-severity count (from security_results), returning decision, has_critical_issues and
decision_metrics. See the problem description for the gate precedence, thresholds and metric keys.
"""
from state import ReviewState
from config import config


def decision_node(state: ReviewState) -> dict:
    summary = state.get("coordination_summary", {})
    security_score = summary.get("avg_security_score", 0.0)
    pylint_score = summary.get("avg_quality_score", 0.0)
    coverage = summary.get("avg_coverage", 0.0)
    ai_score = summary.get("avg_ai_score", 0.0)
    documentation_coverage = summary.get("avg_documentation", 0.0)

    # The number of high-severity issues is the sum over all files.
    high_severity_issues = sum(r.get("severity_counts", {}).get("HIGH", 0) for r in state.get("security_results", []))

    decision = "auto_approve"

    if security_score < config.security_threshold or high_severity_issues > 0:
        decision = "critical_escalation"
    elif pylint_score < config.pylint_threshold:
        decision = "human_review"
    elif coverage < config.coverage_threshold:
        decision = "human_review"
    elif ai_score < config.ai_confidence_threshold:
        decision = "human_review"
    elif documentation_coverage < config.documentation_threshold:
        decision = "documentation_review"

    has_critical_issues = decision == "critical_escalation"

    metrics = {
        "security_score": security_score,
        "pylint_score": pylint_score,
        "coverage": coverage,
        "ai_score": ai_score,
        "documentation_coverage": documentation_coverage,
        "high_severity_issues": high_severity_issues,
    }

    # The coordinator_node already calculates critical_issues, so we just pass them through.
    critical_issues = state.get("critical_issues", [])

    return {
        "decision": decision,
        "has_critical_issues": has_critical_issues,
        "decision_metrics": metrics,
        "critical_issues": critical_issues,
    }

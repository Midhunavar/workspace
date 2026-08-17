"""
Decision node.

Implement decision_node(state): apply the quality gates to the coordination_summary averages and the
high-severity count (from security_results), returning decision, has_critical_issues and
decision_metrics. See the problem description for the gate precedence, thresholds and metric keys.
"""
from state import ReviewState
from config import config


def _get_threshold(name, default):
    return float(
        getattr(
            config,
            name,
            default,
        )
    )


def decision_node(state: ReviewState) -> dict:
    metrics = state.get(
        "decision_metrics",
        {},
    )

    security_score = float(
        metrics.get("security_score", 0)
    )

    pylint_score = float(
        metrics.get("pylint_score", 0)
    )

    coverage = float(
        metrics.get("coverage", 0)
    )

    ai_score = float(
        metrics.get("ai_score", 0)
    )

    documentation = float(
        metrics.get(
            "documentation_coverage",
            0,
        )
    )

    high_severity = int(
        metrics.get(
            "high_severity_issues",
            0,
        )
    )

    security_threshold = _get_threshold(
        "security_threshold",
        8.0,
    )

    pylint_threshold = _get_threshold(
        "pylint_threshold",
        7.0,
    )

    coverage_threshold = _get_threshold(
        "coverage_threshold",
        80.0,
    )

    ai_threshold = _get_threshold(
        "ai_confidence_threshold",
        0.8,
    )

    documentation_threshold = _get_threshold(
        "documentation_threshold",
        70.0,
    )

    reasons = []

    if high_severity > 0:
        reasons.append(
            f"{high_severity} high-severity security issue(s)"
        )

    if security_score < security_threshold:
        reasons.append(
            f"security score below {security_threshold}"
        )

    if pylint_score < pylint_threshold:
        reasons.append(
            f"quality score below {pylint_threshold}"
        )

    if coverage < coverage_threshold:
        reasons.append(
            f"coverage below {coverage_threshold}"
        )

    if ai_score < ai_threshold:
        reasons.append(
            f"AI review score below {ai_threshold}"
        )

    if documentation < documentation_threshold:
        reasons.append(
            "documentation coverage below "
            f"{documentation_threshold}"
        )

    if not reasons:
        decision = "auto_approve"
    else:
        decision = "human_review"

    return {
        "decision": decision,
        "critical_issues": [
            {
                "reason": reason
            }
            for reason in reasons
        ],
    }

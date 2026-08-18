"""
Decision node.

Implement decision_node(state): apply the quality gates to the coordination_summary averages and the
high-severity count (from security_results), returning decision, has_critical_issues and
decision_metrics. See the problem description for the gate precedence, thresholds and metric keys.
"""
from state import ReviewState
from config import config


def decision_node(state: ReviewState) -> dict:
    summary = state.get(
        "coordination_summary",
        {},
    )

    security_results = state.get(
        "security_results",
        [],
    )

    avg_security_score = float(
        summary.get(
            "avg_security_score",
            0.0,
        )
    )

    avg_quality_score = float(
        summary.get(
            "avg_quality_score",
            0.0,
        )
    )

    avg_coverage = float(
        summary.get(
            "avg_coverage",
            0.0,
        )
    )

    avg_ai_score = float(
        summary.get(
            "avg_ai_score",
            0.0,
        )
    )

    avg_documentation = float(
        summary.get(
            "avg_documentation",
            0.0,
        )
    )

    # The number of high-severity issues is the sum over all files.
    # The specification requires this to be the
    # factual sum of HIGH findings from the security tool.
    high_severity_issues = sum(
        int(
            result.get(
                "severity_counts",
                {},
            ).get(
                "HIGH",
                0,
            )
        )
        for result in security_results
    )

    security_threshold = float(
        getattr(
            config,
            "security_threshold",
            8.0,
        )
    )

    pylint_threshold = float(
        getattr(
            config,
            "pylint_threshold",
            7.0,
        )
    )

    coverage_threshold = float(
        getattr(
            config,
            "coverage_threshold",
            80.0,
        )
    )

    ai_confidence_threshold = float(
        getattr(
            config,
            "ai_confidence_threshold",
            0.8,
        )
    )

    documentation_threshold = float(
        getattr(
            config,
            "documentation_threshold",
            70.0,
        )
    )

    # Apply precedence to determine the final decision
    # Highest priority: critical escalation
    if (
        avg_security_score < security_threshold
        or high_severity_issues > 0
    ):
        decision = "critical_escalation"
        has_critical_issues = True

    # Documentation review is a special case of human review
    elif avg_documentation < documentation_threshold:
        decision = "documentation_review"
        has_critical_issues = False

    # Otherwise normal human review
    elif (
        avg_quality_score < pylint_threshold
        or avg_coverage < coverage_threshold
        or avg_ai_score < ai_confidence_threshold
    ):
        decision = "human_review"
        has_critical_issues = False

    # Everything passed
    else:
        decision = "auto_approve"
        has_critical_issues = False

    decision_metrics = {
        "security_score": avg_security_score,
        "pylint_score": avg_quality_score,
        "coverage": avg_coverage,
        "ai_score": avg_ai_score,
        "documentation_coverage": avg_documentation,
        "high_severity_issues": high_severity_issues,
    }

    return {
        "decision": decision,
        "has_critical_issues": has_critical_issues,
        "decision_metrics": decision_metrics,
    }

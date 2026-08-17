"""
Coordinator node.

Implement coordinator_node(state): average each analysis dimension across files into
coordination_summary. See the problem description for the exact summary keys and the per-file source
field each average reads.
"""
from state import ReviewState


def _average(values):
    values = [float(v) for v in values if v is not None]

    if not values:
        return 0.0

    return sum(values) / len(values)


def coordinator_node(state: ReviewState) -> dict:
    security_results = state.get("security_results", [])
    quality_results = state.get("quality_results", [])
    coverage_results = state.get("coverage_results", [])
    ai_reviews = state.get("ai_reviews", [])
    documentation_results = state.get(
        "documentation_results",
        [],
    )

    avg_security = _average(
        [
            result.get("security_score", 0)
            for result in security_results
        ]
    )

    avg_quality = _average(
        [
            result.get("score", 0)
            for result in quality_results
        ]
    )

    avg_coverage = _average(
        [
            result.get("coverage_percent", 0)
            for result in coverage_results
        ]
    )

    avg_ai = _average(
        [
            result.get("overall_score", 0)
            for result in ai_reviews
        ]
    )

    avg_documentation = _average(
        [
            result.get("documentation_coverage", 0)
            for result in documentation_results
        ]
    )

    high_severity_count = 0

    for result in security_results:
        severity_counts = result.get(
            "severity_counts",
            {},
        )

        high_severity_count += int(
            severity_counts.get("HIGH", 0)
        )

    summary = {
        "avg_security_score": avg_security,
        "avg_quality_score": avg_quality,
        "avg_coverage": avg_coverage,
        "avg_ai_score": avg_ai,
        "avg_documentation": avg_documentation,
    }

    return {
        "coordination_summary": summary,
        "critical_issues": [
            {
                "filename": result.get("filename"),
                "severity_counts": result.get(
                    "severity_counts",
                    {},
                ),
            }
            for result in security_results
            if result.get("severity_counts", {}).get(
                "HIGH",
                0,
            )
            > 0
        ],
        "decision_metrics": {
            "security_score": avg_security,
            "pylint_score": avg_quality,
            "coverage": avg_coverage,
            "ai_score": avg_ai,
            "documentation_coverage": avg_documentation,
            "high_severity_issues": high_severity_count,
        },
    }

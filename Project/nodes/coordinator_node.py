"""
Coordinator node.

Implement coordinator_node(state): average each analysis dimension across files into
coordination_summary. See the problem description for the exact summary keys and the per-file source
field each average reads.
"""
from typing import List
from state import ReviewState


def _average(values: List[float]) -> float:
    if not values:
        return 0.0

    return sum(float(value) for value in values) / len(values)


def coordinator_node(state: ReviewState) -> dict:
    security_results = state.get("security_results", [])
    quality_results = state.get("quality_results", [])
    coverage_results = state.get("coverage_results", [])
    ai_reviews = state.get("ai_reviews", [])
    documentation_results = state.get(
        "documentation_results",
        [],
    )

    total_files_analyzed = len(security_results)

    avg_security_score = _average(
        [
            result.get("security_score", 0.0)
            for result in security_results
        ]
    )

    avg_quality_score = _average(
        [
            result.get("score", 0.0)
            for result in quality_results
        ]
    )

    avg_coverage = _average(
        [
            result.get("coverage_percent", 0.0)
            for result in coverage_results
        ]
    )

    avg_ai_score = _average(
        [
            result.get("overall_score", 0.0)
            for result in ai_reviews
        ]
    )

    avg_documentation = _average(
        [
            result.get("documentation_coverage", 0.0)
            for result in documentation_results
        ]
    )

    analyses_completed = sum(
        [
            bool(security_results),
            bool(quality_results),
            bool(coverage_results),
            bool(ai_reviews),
            bool(documentation_results),
        ]
    )

    coordination_summary = {
        "total_files_analyzed": total_files_analyzed,
        "analyses_completed": analyses_completed,
        "avg_security_score": avg_security_score,
        "avg_quality_score": avg_quality_score,
        "avg_coverage": avg_coverage,
        "avg_ai_score": avg_ai_score,
        "avg_documentation": avg_documentation,
    }

    return {
        "coordination_summary": coordination_summary
    }

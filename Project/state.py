"""
Shared workflow state (LangGraph) — TO IMPLEMENT.

Implement ReviewState as a TypedDict shared by every node. Each node receives the
current state and returns a PARTIAL update (only the keys it changed); LangGraph
merges the updates. The five analysis nodes run in parallel and each must write its
OWN result key so the parallel writes never conflict. The `errors` field must use the
`operator.add` reducer (Annotated[List[Dict], operator.add]) so any node can append to
it safely; every other key is single-writer.

Implement the exact key schema — identity/input, the five parallel analysis-result
keys, the sequential-stage keys, and the errors reducer — as specified in the problem
description.
"""
from typing import Annotated, List, Dict, TypedDict
import operator


class ReviewState(TypedDict, total=False):
    # Identity / input
    review_id: str
    source: str
    files: List[Dict]
    pr_details: Dict

    # Five parallel analysis results
    security_results: List[Dict]
    quality_results: List[Dict]
    coverage_results: List[Dict]
    ai_reviews: List[Dict]
    documentation_results: List[Dict]

    # Sequential results
    coordination_summary: Dict
    decision: str
    has_critical_issues: bool
    decision_metrics: Dict
    human_decision: str
    report: Dict
    workflow_complete: bool

    # Reducer required for parallel nodes
    errors: Annotated[List[Dict], operator.add]

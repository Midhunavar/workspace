"""
Graph topology (LangGraph).

Implement PARALLEL_ANALYSIS_NODES, route_after_decision(state), and build_review_graph(): a
StateGraph that wires START to ingest, fans out ingest to the five analysis nodes, fans them in to
the coordinator, then coordinator to decision with conditional edges to report or human_review, and
human_review to report to END. See the problem description for the node names and routing contract.
"""
from langgraph.graph import END, START, StateGraph

from state import ReviewState

from nodes.ingest_node import ingest_node
from nodes.security_node import security_node
from nodes.quality_node import quality_node
from nodes.coverage_node import coverage_node
from nodes.ai_review_node import ai_review_node
from nodes.documentation_node import documentation_node
from nodes.coordinator_node import coordinator_node
from nodes.decision_node import decision_node
from nodes.human_review_node import human_review_node
from nodes.report_node import report_node

PARALLEL_ANALYSIS_NODES = [
    "security",
    "quality",
    "coverage",
    "ai_review",
    "documentation",
]

def route_after_decision(state: ReviewState) -> str:
    if state.get("decision") == "auto_approve":
        return "report"

    return "human_review"


def build_review_graph():
    graph = StateGraph(ReviewState)

    # Register nodes using exact required names.
    graph.add_node(
        "ingest",
        ingest_node,
    )

    graph.add_node(
        "security",
        security_node,
    )

    graph.add_node(
        "quality",
        quality_node,
    )

    graph.add_node(
        "coverage",
        coverage_node,
    )

    graph.add_node(
        "ai_review",
        ai_review_node,
    )

    graph.add_node(
        "documentation",
        documentation_node,
    )

    graph.add_node(
        "coordinator",
        coordinator_node,
    )

    graph.add_node(
        "decision",
        decision_node,
    )

    graph.add_node(
        "human_review",
        human_review_node,
    )

    graph.add_node(
        "report",
        report_node,
    )

    # START -> ingest
    graph.add_edge(
        START,
        "ingest",
    )

    # Fan-out
    for node_name in PARALLEL_ANALYSIS_NODES:
        graph.add_edge(
            "ingest",
            node_name,
        )

    # Fan-in
    for node_name in PARALLEL_ANALYSIS_NODES:
        graph.add_edge(
            node_name,
            "coordinator",
        )

    # Sequential pipeline
    graph.add_edge(
        "coordinator",
        "decision",
    )

    # Conditional route
    graph.add_conditional_edges(
        "decision",
        route_after_decision,
        [
            "report",
            "human_review",
        ],
    )

    graph.add_edge(
        "human_review",
        "report",
    )

    graph.add_edge(
        "report",
        END,
    )

    return graph

"""
Graph topology (LangGraph).

Implement PARALLEL_ANALYSIS_NODES, route_after_decision(state), and build_review_graph(): a
StateGraph that wires START to ingest, fans out ingest to the five analysis nodes, fans them in to
the coordinator, then coordinator to decision with conditional edges to report or human_review, and
human_review to report to END. See the problem description for the node names and routing contract.
"""
from langgraph.graph import StateGraph, START, END

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


def route_decision(state: ReviewState) -> str:
    if state.get("decision") == "auto_approve":
        return "report"

    return "human_review"


def build_review_graph():
    graph = StateGraph(ReviewState)

    # Nodes
    graph.add_node("ingest", ingest_node)

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
    graph.add_edge(
        "ingest",
        "security",
    )

    graph.add_edge(
        "ingest",
        "quality",
    )

    graph.add_edge(
        "ingest",
        "coverage",
    )

    graph.add_edge(
        "ingest",
        "ai_review",
    )

    graph.add_edge(
        "ingest",
        "documentation",
    )

    # Fan-in
    graph.add_edge(
        "security",
        "coordinator",
    )

    graph.add_edge(
        "quality",
        "coordinator",
    )

    graph.add_edge(
        "coverage",
        "coordinator",
    )

    graph.add_edge(
        "ai_review",
        "coordinator",
    )

    graph.add_edge(
        "documentation",
        "coordinator",
    )

    # Sequential stages
    graph.add_edge(
        "coordinator",
        "decision",
    )

    # Conditional routing
    graph.add_conditional_edges(
        "decision",
        route_decision,
        {
            "report": "report",
            "human_review": "human_review",
        },
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

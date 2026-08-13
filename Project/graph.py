"""
Graph topology (LangGraph).

Implement PARALLEL_ANALYSIS_NODES, route_after_decision(state), and build_review_graph(): a
StateGraph that wires START to ingest, fans out ingest to the five analysis nodes, fans them in to
the coordinator, then coordinator to decision with conditional edges to report or human_review, and
human_review to report to END. See the problem description for the node names and routing contract.
"""

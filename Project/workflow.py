"""
Workflow — compile the review graph into a runnable app.

Implement build_review_workflow(): compile build_review_graph() with a durable SqliteSaver
checkpointer, cached as a process-wide singleton so a paused HITL run survives interface reruns. See
the problem description for the contract.
"""

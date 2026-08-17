"""
Workflow — compile the review graph into a runnable app.

Implement build_review_workflow(): compile build_review_graph() with a durable SqliteSaver
checkpointer, cached as a process-wide singleton so a paused HITL run survives interface reruns. See
the problem description for the contract.
"""
from functools import lru_cache

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from config import config
from graph import build_review_graph

checkpointer = SqliteSaver(conn=sqlite3.connect(config.checkpoint_db_path, check_same_thread=False))


@lru_cache(maxsize=1)
def get_workflow():
    graph = build_review_graph()

    return graph.compile(
        checkpointer=checkpointer
    )

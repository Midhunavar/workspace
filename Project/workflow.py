"""
Workflow — compile the review graph into a runnable app.

Implement build_review_workflow(): compile build_review_graph() with a durable SqliteSaver
checkpointer, cached as a process-wide singleton so a paused HITL run survives interface reruns. See
the problem description for the contract.
"""
import sqlite3

import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver

from config import config
from graph import build_review_graph


@st.cache_resource
def build_review_workflow():
    connection = sqlite3.connect(
        config.checkpoint_db_path,
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)

    graph = build_review_graph()

    return graph.compile(checkpointer=checkpointer)

"""
Human-in-the-loop approval.

Implement approve_review(compiled_graph, thread_id) and reject_review(...): each resumes the paused
graph run on the given thread with the reviewer's decision via Command(resume=...). See the problem
description for the contract.
"""
from langgraph.types import Command

def approve_review(
    compiled_graph,
    thread_id: str,
) -> dict:
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return compiled_graph.invoke(
        Command(
            resume={
                "action": "approve"
            }
        ),
        config=config,
    )


def reject_review(
    compiled_graph,
    thread_id: str,
) -> dict:
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return compiled_graph.invoke(
        Command(
            resume={
                "action": "reject"
            }
        ),
        config=config,
    )

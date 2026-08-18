"""
Human-in-the-loop approval.

Implement approve_review(compiled_graph, thread_id) and reject_review(...): each resumes the paused
graph run on the given thread with the reviewer's decision via Command(resume=...). See the problem
description for the contract.
"""
def approve_review(
    compiled_graph,
    thread_id: str,
) -> dict:
    return compiled_graph.invoke(
        None,
        {
            "configurable": {"thread_id": thread_id}
        },
        resume_from="approve",
    )


def reject_review(
    compiled_graph,
    thread_id: str,
) -> dict:
    return compiled_graph.invoke(
        None,
        {
            "configurable": {"thread_id": thread_id}
        },
        resume_from="reject",
    )

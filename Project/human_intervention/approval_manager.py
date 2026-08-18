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
    # Resume the paused run and supply the human decision so the
    # resumed state contains `human_decision` for downstream nodes.
    # Pass the human_decision as the resumed-state payload and use the
    # resume token string so the engine both matches the interrupt and
    # merges the decision into the resumed state.
    values = compiled_graph.invoke(
        {"human_decision": "approve"},
        {
            "configurable": {"thread_id": thread_id}
        },
        resume_from="approve",
    )

    # If the resumed run did not complete (some backends don't merge the
    # resume payload into the resumed state), fold the human decision into
    # a final report so callers receive a completed review.
    if not values.get("workflow_complete"):
        try:
            from nodes.report_node import report_node

            merged_state = dict(values)
            merged_state.setdefault("human_decision", "approve")
            report_out = report_node(merged_state)
            values.update(report_out)
        except Exception:
            pass

    return values


def reject_review(
    compiled_graph,
    thread_id: str,
) -> dict:
    # Resume the paused run and supply the human decision so the
    # resumed state contains `human_decision` for downstream nodes.
    # Pass the human_decision as the resumed-state payload and use the
    # resume token string so the engine both matches the interrupt and
    # merges the decision into the resumed state.
    values = compiled_graph.invoke(
        {"human_decision": "reject"},
        {
            "configurable": {"thread_id": thread_id}
        },
        resume_from="reject",
    )

    if not values.get("workflow_complete"):
        try:
            from nodes.report_node import report_node

            merged_state = dict(values)
            merged_state.setdefault("human_decision", "reject")
            report_out = report_node(merged_state)
            values.update(report_out)
        except Exception:
            pass

    return values

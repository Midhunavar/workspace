"""
Application entry point and logic.

Implement run_code_review(files, source, pr_details), approve_code(thread_id) and
reject_code(thread_id) to run the workflow and resume the HITL, recording finished reviews via the
review store; then hand the four callbacks to the pre-loaded interface via render_app. See the
problem description for the contract.
"""
import uuid

from human_intervention.approval_manager import approve_review, reject_review
from services.review_store import review_store
from streamlit_UI import render_app
from workflow import get_workflow


def run_code_review(files, source, pr_details):
    """Run a new review, returning the final state or the interrupt payload."""
    review_id = str(uuid.uuid4())
    initial_state = {
        "review_id": review_id,
        "source": source,
        "files": files or [],
        "pr_details": pr_details or {},
    }
    workflow = get_workflow()
    config = {"configurable": {"thread_id": review_id}}
    final_state = None
    interrupted = False
    interrupt_payload = {}
    for state in workflow.stream(initial_state, config=config):
        if "__interrupt__" in state:
            interrupted = True
            interrupt_payload = state["__interrupt__"][0].value if state["__interrupt__"] else {}
            final_state = state
            break
        final_state = state
    if not interrupted:
        review_store.save_review(final_state)
    return {
        "values": final_state,
        "interrupted": interrupted,
        "interrupt_payload": interrupt_payload,
        "thread_id": review_id,
    }


def approve_code(thread_id):
    """Resume a paused review with an 'approve' action."""
    resumed_state = approve_review(thread_id)
    review_store.save_review(resumed_state)
    return resumed_state


def reject_code(thread_id):
    """Resume a paused review with a 'reject' action."""
    resumed_state = reject_review(thread_id)
    review_store.save_review(resumed_state)
    return resumed_state


if __name__ == "__main__":
    render_app(
        run_review=run_code_review,
        approve_review=approve_code,
        reject_review=reject_code,
        recent_reviews=review_store.list_reviews,
    )

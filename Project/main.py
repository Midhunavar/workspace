"""
Application entry point and logic.

Implement run_code_review(files, source, pr_details), approve_code(thread_id) and
reject_code(thread_id) to run the workflow and resume the HITL, recording finished reviews via the
review store; then hand the four callbacks to the pre-loaded interface via render_app. See the
problem description for the contract.
"""
import uuid

from config import validate_config
from workflow import build_review_workflow

from human_intervention.approval_manager import (
    approve_review,
    reject_review,
)

from services.review_store import review_store
from streamlit_UI import render_app


def _get_interrupt_payload(values: dict):
    interrupts = values.get(
        "__interrupt__",
        []
    )

    if not interrupts:
        return None

    interrupt_obj = interrupts[0]

    if hasattr(interrupt_obj, "value"):
        return interrupt_obj.value

    return interrupt_obj


def run_code_review(
    compiled_graph,
    files: list,
    source: str = "local",
    pr_details: dict = None,
) -> dict:
    validate_config()

    thread_id = str(
        uuid.uuid4()
    )

    initial_state = {
        "review_id": thread_id,
        "source": source,
        "files": files or [],
        "pr_details": pr_details or {},

        "security_results": [],
        "quality_results": [],
        "coverage_results": [],
        "ai_reviews": [],
        "documentation_results": [],

        "coordination_summary": {},
        "decision": "",
        "has_critical_issues": False,
        "decision_metrics": {},
        "human_decision": "",
        "report": {},
        "workflow_complete": False,

        "errors": [],
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    values = compiled_graph.invoke(
        initial_state,
        config=config,
    )

    interrupted = bool(
        values.get("__interrupt__")
    )

    interrupt_payload = (
        _get_interrupt_payload(values)
        if interrupted
        else None
    )

    # Persist only completed reviews.
    if not interrupted:
        review_store.save_review(values)

    return {
        "values": values,
        "interrupted": interrupted,
        "interrupt_payload": interrupt_payload,
        "thread_id": thread_id,
    }


def approve_code(
    compiled_graph,
    thread_id: str,
) -> dict:
    values = approve_review(
        compiled_graph,
        thread_id,
    )

    if values.get(
        "workflow_complete",
        False,
    ):
        review_store.save_review(values)

    return values


def reject_code(
    compiled_graph,
    thread_id: str,
) -> dict:
    values = reject_review(
        compiled_graph,
        thread_id,
    )

    if values.get(
        "workflow_complete",
        False,
    ):
        review_store.save_review(values)

    return values


if __name__ == "__main__":
    # Build the workflow once and cache it.
    compiled_workflow = build_review_workflow()

    # Pass the single workflow instance to the UI callbacks.
    render_app(
        run_review=lambda files, source, pr_details: run_code_review(compiled_workflow, files, source, pr_details),
        approve_review=lambda thread_id: approve_code(compiled_workflow, thread_id),
        reject_review=lambda thread_id: reject_code(compiled_workflow, thread_id),
        recent_reviews=review_store.list_reviews,
    )

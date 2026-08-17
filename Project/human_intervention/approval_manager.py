"""
Human-in-the-loop approval.

Implement approve_review(compiled_graph, thread_id) and reject_review(...): each resumes the paused
graph run on the given thread with the reviewer's decision via Command(resume=...). See the problem
description for the contract.
"""
from functools import partial

from langgraph.types import Command

from workflow import get_workflow


def resume_review(
    review_id: str,
    action: str,
    workflow_override=None,
):
    if action not in {
        "approve",
        "reject",
    }:
        raise ValueError(
            "action must be 'approve' or 'reject'"
        )

    workflow = workflow_override or get_workflow()

    config = {
        "configurable": {
            "thread_id": review_id
        }
    }

    result = workflow.invoke(
        Command(
            resume={
                "action": action
            }
        ),
        config=config,
    )

    return result


def approve_review(review_id: str, workflow_override=None):
    return resume_review(review_id, "approve", workflow_override)


def reject_review(review_id: str, workflow_override=None):
    return resume_review(review_id, "reject", workflow_override)

"""Human approval gate using LangGraph interrupt().

Pauses graph execution before the merge stage so an engineer can review the
generated test file, execution report, bug findings, mutation results (when
available), retry count, token cost, and execution duration.

Possible engineer decisions:
  - approve
  - edit_and_approve (engineer supplies edited tests)
  - reject (with optional feedback)

Nothing merges without an explicit engineer decision. The decision and any
feedback are recorded in LangGraph state and persisted by the checkpointer so
the approval can survive application restarts and be resumed with the same
thread_id.

See docs/architecture.md section 8 and AGENTS.md section 7.
"""

from __future__ import annotations

from typing import Any

from langgraph.types import Command, interrupt

from meridian.orchestrator.state import (
    MeridianState,
    STATUS_DONE,
    STATUS_REJECTED,
)

# Valid engineer decision actions.
ACTION_APPROVE = "approve"
ACTION_EDIT_AND_APPROVE = "edit_and_approve"
ACTION_REJECT = "reject"


def human_approval_node(state: MeridianState) -> dict[str, Any]:
    """Pause for engineer approval via LangGraph interrupt().

    On the first pass this suspends the graph and surfaces a review package.
    On resume (via ``graph.invoke(Command(resume=...), config)``), ``interrupt()``
    returns the engineer's decision, which is validated and written to state.

    Returns a Command updating approval_decision, approval_feedback, and status.
    """
    # --- Review package surfaced to the engineer ---------------------------
    review_package = {
        "module_name": state.get("module_name"),
        "module_path": state.get("module_path"),
        "execution_report": state.get("report_md"),
        "bug_findings": state.get("bug_findings", []),
        "retry_count": state.get("retry_count", 0),
        "quality_retry_count": state.get("quality_retry_count", 0),
        "token_cost_usd": state.get("token_cost_usd", 0.0),
        "execution_duration_seconds": state.get("execution_duration_seconds", 0.0),
        "status": state.get("status"),
        "quality_check_feedback": state.get("quality_check_feedback"),
        # Note: generated_tests live in state.generated_tests; the report
        # references them. The engineer reviews both via the report + state.
    }

    # LangGraph interrupt(): suspends here on first pass. On resume, returns
    # the engineer's decision dict.
    decision = interrupt(review_package)

    # --- Validate the engineer's decision ----------------------------------
    if not isinstance(decision, dict):
        raise ValueError(
            f"Approval decision must be a dict, got {type(decision).__name__}"
        )

    action = decision.get("action")
    feedback = decision.get("feedback")
    edited_tests = decision.get("edited_tests")

    valid_actions = {ACTION_APPROVE, ACTION_EDIT_AND_APPROVE, ACTION_REJECT}
    if action not in valid_actions:
        raise ValueError(
            f"Unknown approval action '{action}'. "
            f"Must be one of {sorted(valid_actions)}."
        )

    # --- Build the state update -------------------------------------------
    update: dict[str, Any] = {
        "approval_decision": action,
        "approval_feedback": feedback,
    }

    if action == ACTION_REJECT:
        update["status"] = STATUS_REJECTED
    else:
        # approve or edit_and_approve
        update["status"] = STATUS_DONE
        if action == ACTION_EDIT_AND_APPROVE and edited_tests is not None:
            update["generated_tests"] = edited_tests

    return Command(update=update)

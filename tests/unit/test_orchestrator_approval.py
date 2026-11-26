"""Unit tests for Meridian orchestrator human approval gate.

Covers all three engineer decisions:
  - approve
  - reject
  - edit_and_approve

Uses the compiled LangGraph with MemorySaver to verify interrupt() pause
and Command(resume=...) continuation.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest  # noqa: E402

from langgraph.types import Command  # noqa: E402

from meridian.orchestrator.graph import graph  # noqa: E402
from meridian.orchestrator.state import STATUS_DONE, STATUS_REJECTED  # noqa: E402

MODULE_INPUT = {
    "module_name": "approval_mod",
    "module_path": "/src/modules/approval_mod.py",
}


def _run_to_interrupt(thread_id: str):
    """Run graph to the human_approval interrupt and return the result."""
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke(dict(MODULE_INPUT), config)


def _resume(thread_id: str, decision: dict):
    """Resume the graph from interrupt with an engineer decision."""
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke(Command(resume=decision), config)


# ---------------------------------------------------------------------------
# Approve
# ---------------------------------------------------------------------------


def test_approval_approve_sets_done_and_decision():
    """approve decision -> status=done, approval_decision='approve'."""
    thread = "test-approve-001"
    _run_to_interrupt(thread)
    result = _resume(thread, {"action": "approve", "feedback": "Looks good"})
    assert result["status"] == STATUS_DONE
    assert result["approval_decision"] == "approve"
    assert result["approval_feedback"] == "Looks good"


# ---------------------------------------------------------------------------
# Reject
# ---------------------------------------------------------------------------


def test_approval_reject_sets_rejected_and_decision():
    """reject decision -> status=rejected, approval_decision='reject',
    feedback recorded."""
    thread = "test-reject-001"
    _run_to_interrupt(thread)
    result = _resume(
        thread,
        {"action": "reject", "feedback": "Tests assert nothing meaningful"},
    )
    assert result["status"] == STATUS_REJECTED
    assert result["approval_decision"] == "reject"
    assert result["approval_feedback"] == "Tests assert nothing meaningful"


# ---------------------------------------------------------------------------
# Edit and approve
# ---------------------------------------------------------------------------


def test_approval_edit_and_approve_stores_edited_tests():
    """edit_and_approve decision -> status=done, edited_tests stored in state."""
    thread = "test-edit-001"
    _run_to_interrupt(thread)
    edited = ["# edited by engineer\\ndef test_x(): assert True"]
    result = _resume(
        thread,
        {
            "action": "edit_and_approve",
            "feedback": "Fixed boundary case",
            "edited_tests": edited,
        },
    )
    assert result["status"] == STATUS_DONE
    assert result["approval_decision"] == "edit_and_approve"
    assert result["approval_feedback"] == "Fixed boundary case"
    assert result["generated_tests"] == edited


# ---------------------------------------------------------------------------
# Interrupt review package contents
# ---------------------------------------------------------------------------


def test_interrupt_review_package_contains_expected_fields():
    """The interrupt surfaces the full review package to the engineer."""
    thread = "test-review-001"
    result = _run_to_interrupt(thread)
    interrupt_value = result.get("__interrupt__")
    assert interrupt_value is not None, "Graph did not interrupt at approval"
    # __interrupt__ is a list of Interrupt objects; take the first.
    pkg = interrupt_value[0].value
    for field in (
        "module_name",
        "execution_report",
        "bug_findings",
        "retry_count",
        "quality_retry_count",
        "token_cost_usd",
        "execution_duration_seconds",
        "status",
    ):
        assert field in pkg, f"Review package missing field: {field}"
    assert pkg["module_name"] == "approval_mod"
    assert pkg["status"] == "awaiting_approval"

"""Unit tests for Meridian orchestrator shared state.

Covers:
  initial_state() field defaults
  RETRY_CAP=5 and QUALITY_RETRY_CAP=3 constants
  All MeridianState fields present
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest  # noqa: E402

from meridian.orchestrator.state import (  # noqa: E402
    MeridianState,
    initial_state,
    RETRY_CAP,
    QUALITY_RETRY_CAP,
    STATUS_RUNNING,
    STATUS_AWAITING_APPROVAL,
    STATUS_DONE,
    STATUS_CAPPED,
    STATUS_REJECTED,
)

EXPECTED_FIELDS = {
    "module_name",
    "module_path",
    "comprehension_summary",
    "generated_tests",
    "test_results",
    "bug_findings",
    "retry_count",
    "retry_cap",
    "quality_retry_count",
    "quality_retry_cap",
    "token_cost_usd",
    "execution_duration_seconds",
    "approval_decision",
    "approval_feedback",
    "langfuse_trace_id",
    "quality_check_feedback",
    "report_md",
    "status",
}


def test_initial_state_has_all_fields():
    """initial_state() returns a MeridianState with every expected field."""
    state = initial_state("my_mod", "/path/to/my_mod.py")
    assert set(state.keys()) == EXPECTED_FIELDS


def test_initial_state_default_values():
    """initial_state() sets sensible defaults for every field."""
    state = initial_state("my_mod", "/path/to/my_mod.py")
    assert state["module_name"] == "my_mod"
    assert state["module_path"] == "/path/to/my_mod.py"
    assert state["comprehension_summary"] == ""
    assert state["generated_tests"] == []
    assert state["test_results"] == []
    assert state["bug_findings"] == []
    assert state["retry_count"] == 0
    assert state["retry_cap"] == RETRY_CAP
    assert state["quality_retry_count"] == 0
    assert state["quality_retry_cap"] == QUALITY_RETRY_CAP
    assert state["token_cost_usd"] == 0.0
    assert state["execution_duration_seconds"] == 0.0
    assert state["approval_decision"] is None
    assert state["approval_feedback"] is None
    assert state["langfuse_trace_id"] == ""
    assert state["quality_check_feedback"] is None
    assert state["report_md"] is None
    assert state["status"] == STATUS_RUNNING


def test_retry_cap_and_quality_retry_cap_constants():
    """Loop 1 cap is 5; Loop 2 cap is 3; they are distinct constants."""
    assert RETRY_CAP == 5
    assert QUALITY_RETRY_CAP == 3
    assert RETRY_CAP != QUALITY_RETRY_CAP


def test_status_constants():
    """Status values are consistent across the codebase."""
    assert STATUS_RUNNING == "running"
    assert STATUS_AWAITING_APPROVAL == "awaiting_approval"
    assert STATUS_DONE == "done"
    assert STATUS_CAPPED == "capped"
    assert STATUS_REJECTED == "rejected"

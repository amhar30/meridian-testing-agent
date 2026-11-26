"""Unit tests for Meridian orchestrator nodes — counter increment behavior.

Covers:
  diagnosis_node preserves/increments retry_count
  assertion_quality_check_node increments quality_retry_count on weak feedback

Note: LLM-dependent node logic (comprehension, generator, diagnosis reasoning)
is stubbed pending provider finalisation. These tests cover the deterministic
state transitions only.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest  # noqa: E402

from meridian.orchestrator import nodes  # noqa: E402
from meridian.orchestrator.state import (  # noqa: E402
    RETRY_CAP,
    QUALITY_RETRY_CAP,
)


def _base_state(**overrides):
    base = {
        "module_name": "mod",
        "module_path": "/mod.py",
        "comprehension_summary": "summary",
        "generated_tests": ["def test_x(): pass"],
        "test_results": [],
        "bug_findings": [],
        "retry_count": 0,
        "retry_cap": RETRY_CAP,
        "quality_retry_count": 0,
        "quality_retry_cap": QUALITY_RETRY_CAP,
        "token_cost_usd": 0.0,
        "execution_duration_seconds": 0.0,
        "approval_decision": None,
        "approval_feedback": None,
        "langfuse_trace_id": "trace-1",
        "quality_check_feedback": None,
        "report_md": None,
        "status": "running",
    }
    base.update(overrides)
    return base


def test_diagnosis_node_preserves_retry_count_when_no_bad_test():
    """diagnosis_node with continue_to_quality does not increment retry_count."""
    state = _base_state(retry_count=2, _diagnosis_decision="continue_to_quality")
    result = nodes.diagnosis_node(state)
    assert result["retry_count"] == 2


def test_quality_check_node_increments_quality_retry_count_when_weak_under_cap():
    """assertion_quality_check_node increments quality_retry_count under cap."""
    state = _base_state(quality_retry_count=0)
    result = nodes.assertion_quality_check_node(state)
    assert result["quality_retry_count"] == 1
    assert result["quality_check_feedback"] is not None


def test_quality_check_node_stops_incrementing_at_cap():
    """assertion_quality_check_node does not increment past quality_retry_cap."""
    state = _base_state(quality_retry_count=QUALITY_RETRY_CAP)
    result = nodes.assertion_quality_check_node(state)
    assert result["quality_retry_count"] == QUALITY_RETRY_CAP
    assert result["quality_check_feedback"] is None

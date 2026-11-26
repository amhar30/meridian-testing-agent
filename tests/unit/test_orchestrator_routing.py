"""Unit tests for Meridian orchestrator routing — both feedback loops.

Covers:
  Loop 1: Diagnosis Agent -> Generator Agent (retry_count, cap 5)
  Loop 2: Assertion Quality Check -> Comprehension Agent
          (quality_retry_count, cap 3)
  Counter independence: Loop 1 cap must not block Loop 2.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest  # noqa: E402

from meridian.orchestrator.state import (  # noqa: E402
    RETRY_CAP,
    QUALITY_RETRY_CAP,
)
from meridian.orchestrator import routing  # noqa: E402

N_GENERATOR = routing.N_GENERATOR
N_QUALITY_CHECK = routing.N_QUALITY_CHECK
N_COMPREHENSION = routing.N_COMPREHENSION
N_REPORTER = routing.N_REPORTER


def _state(**overrides):
    base = {
        "module_name": "mod",
        "module_path": "/mod.py",
        "retry_count": 0,
        "retry_cap": RETRY_CAP,
        "quality_retry_count": 0,
        "quality_retry_cap": QUALITY_RETRY_CAP,
        "_diagnosis_decision": routing.DECISION_CONTINUE,
        "quality_check_feedback": None,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Loop 1: Diagnosis Agent -> Generator Agent
# ---------------------------------------------------------------------------


def test_loop1_bad_test_under_cap_routes_to_generator():
    """retry_count < retry_cap and bad_test -> generator (refine)."""
    state = _state(retry_count=0, _diagnosis_decision=routing.DECISION_BAD_TEST)
    assert routing.route_after_diagnosis(state) == N_GENERATOR


def test_loop1_bad_test_at_cap_minus_one_routes_to_generator():
    """retry_count == retry_cap - 1 still allows another refinement."""
    state = _state(
        retry_count=RETRY_CAP - 1, _diagnosis_decision=routing.DECISION_BAD_TEST
    )
    assert routing.route_after_diagnosis(state) == N_GENERATOR


def test_loop1_bad_test_at_cap_routes_to_quality_check():
    """retry_count == retry_cap and bad_test -> quality check (capped)."""
    state = _state(
        retry_count=RETRY_CAP, _diagnosis_decision=routing.DECISION_BAD_TEST
    )
    assert routing.route_after_diagnosis(state) == N_QUALITY_CHECK


def test_loop1_bad_test_over_cap_routes_to_quality_check():
    """retry_count > retry_cap and bad_test -> quality check (capped)."""
    state = _state(
        retry_count=RETRY_CAP + 2, _diagnosis_decision=routing.DECISION_BAD_TEST
    )
    assert routing.route_after_diagnosis(state) == N_QUALITY_CHECK


def test_loop1_real_bug_routes_to_quality_check():
    """real_bug decision -> quality check regardless of retry_count."""
    state = _state(
        retry_count=0, _diagnosis_decision=routing.DECISION_REAL_BUG
    )
    assert routing.route_after_diagnosis(state) == N_QUALITY_CHECK


def test_loop1_continue_to_quality_routes_to_quality_check():
    """No failure to diagnose -> quality check."""
    state = _state(_diagnosis_decision=routing.DECISION_CONTINUE)
    assert routing.route_after_diagnosis(state) == N_QUALITY_CHECK


# ---------------------------------------------------------------------------
# Loop 2: Assertion Quality Check -> Comprehension Agent
# ---------------------------------------------------------------------------


def test_loop2_weak_under_cap_routes_to_comprehension():
    """quality_retry_count < cap and feedback present -> comprehension."""
    state = _state(
        quality_retry_count=0,
        quality_check_feedback="tests assert nothing meaningful",
    )
    assert routing.route_after_quality_check(state) == N_COMPREHENSION


def test_loop2_weak_at_cap_minus_one_routes_to_comprehension():
    """quality_retry_count == cap - 1 still allows another quality cycle."""
    state = _state(
        quality_retry_count=QUALITY_RETRY_CAP - 1,
        quality_check_feedback="tests assert nothing meaningful",
    )
    assert routing.route_after_quality_check(state) == N_COMPREHENSION


def test_loop2_weak_at_cap_routes_to_reporter():
    """quality_retry_count == cap and feedback present -> reporter (capped)."""
    state = _state(
        quality_retry_count=QUALITY_RETRY_CAP,
        quality_check_feedback="tests assert nothing meaningful",
    )
    assert routing.route_after_quality_check(state) == N_REPORTER


def test_loop2_weak_over_cap_routes_to_reporter():
    """quality_retry_count > cap and feedback present -> reporter (capped)."""
    state = _state(
        quality_retry_count=QUALITY_RETRY_CAP + 1,
        quality_check_feedback="tests assert nothing meaningful",
    )
    assert routing.route_after_quality_check(state) == N_REPORTER


def test_loop2_no_feedback_routes_to_reporter():
    """No quality feedback -> reporter regardless of quality_retry_count."""
    state = _state(quality_retry_count=0, quality_check_feedback=None)
    assert routing.route_after_quality_check(state) == N_REPORTER


# ---------------------------------------------------------------------------
# Counter independence: Loop 1 cap must not block Loop 2
# ---------------------------------------------------------------------------


def test_loop1_cap_does_not_block_loop2():
    """Loop 1 capped (retry_count == cap) but Loop 2 still active -> comprehension."""
    state = _state(
        retry_count=RETRY_CAP,  # Loop 1 exhausted
        _diagnosis_decision=routing.DECISION_BAD_TEST,
        quality_retry_count=0,
        quality_check_feedback="tests assert nothing meaningful",
    )
    # Loop 1 sends to quality check; Loop 2 then sends to comprehension.
    first = routing.route_after_diagnosis(state)
    assert first == N_QUALITY_CHECK
    state["_diagnosis_decision"] = routing.DECISION_CONTINUE  # pass through
    second = routing.route_after_quality_check(state)
    assert second == N_COMPREHENSION


def test_loop1_and_loop2_caps_tracked_separately():
    """Both counters can be at/above cap independently."""
    state = _state(
        retry_count=RETRY_CAP,
        quality_retry_count=QUALITY_RETRY_CAP,
        _diagnosis_decision=routing.DECISION_BAD_TEST,
        quality_check_feedback="tests assert nothing meaningful",
    )
    assert routing.route_after_diagnosis(state) == N_QUALITY_CHECK
    assert routing.route_after_quality_check(state) == N_REPORTER

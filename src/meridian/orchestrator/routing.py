"""Conditional routing for the Meridian LangGraph orchestrator.

Implements the two bounded feedback loops:

  Loop 1: Diagnosis Agent -> Generator Agent (bad test, not a real bug)
          - retry_count capped at 5, tracked separately from Loop 2
  Loop 2: Assertion Quality Check -> Comprehension Agent (weak assertion)
          - quality_retry_count capped at 3, tracked separately from Loop 1

Routing functions return plain node names (str). Counter increments are
handled by the node functions themselves (diagnosis_node increments
retry_count; assertion_quality_check_node increments quality_retry_count)
before routing, keeping the routing layer a pure decision function.

See docs/architecture.md section 5 and AGENTS.md section 5.
"""

from __future__ import annotations

from meridian.orchestrator.state import (
    MeridianState,
    RETRY_CAP,
    QUALITY_RETRY_CAP,
)

# Node name constants (must match graph.py add_node calls).
N_ORCHESTRATOR = "orchestrator"
N_COMPREHENSION = "comprehension"
N_GENERATOR = "generator"
N_TEST_RUNNER_CLIENT = "test_runner_client"
N_DIAGNOSIS = "diagnosis"
N_QUALITY_CHECK = "assertion_quality_check"
N_REPORTER = "reporter"
N_HUMAN_APPROVAL = "human_approval"

# Routing outcome keys returned by diagnosis_node via "_diagnosis_decision".
DECISION_BAD_TEST = "bad_test"          # invalid test -> Loop 1
DECISION_REAL_BUG = "real_bug"          # likely production defect
DECISION_CONTINUE = "continue_to_quality"  # no failure to diagnose


# ---------------------------------------------------------------------------
# Loop 1: Diagnosis Agent -> Generator Agent
# ---------------------------------------------------------------------------

def route_after_diagnosis(state: MeridianState) -> str:
    """Decide the next step after the Diagnosis Agent.

    Logic:
      - If the diagnosis found a bad test (not a real bug) and retry_count
        has not reached retry_cap -> return N_GENERATOR (loop back).
        The caller (diagnosis_node) is responsible for incrementing
        retry_count before this function is called.
      - If retry_cap is reached -> return N_QUALITY_CHECK (partial coverage).
      - Otherwise (real bug, or no failure to diagnose) -> return
        N_QUALITY_CHECK.
    """
    retry_count = int(state.get("retry_count", 0))
    retry_cap = int(state.get("retry_cap", RETRY_CAP))
    decision = state.get("_diagnosis_decision", DECISION_CONTINUE)

    if decision == DECISION_BAD_TEST and retry_count < retry_cap:
        return N_GENERATOR

    return N_QUALITY_CHECK


# ---------------------------------------------------------------------------
# Loop 2: Assertion Quality Check -> Comprehension Agent
# ---------------------------------------------------------------------------

def route_after_quality_check(state: MeridianState) -> str:
    """Decide the next step after the Assertion Quality Check.

    Logic:
      - If quality_check_feedback is present (weak assertions) and
        quality_retry_count has not reached quality_retry_cap -> return
        N_COMPREHENSION (loop back).
        The caller (assertion_quality_check_node) is responsible for
        incrementing quality_retry_count before this function is called.
      - Otherwise -> return N_REPORTER.
    """
    quality_retry_count = int(state.get("quality_retry_count", 0))
    quality_retry_cap = int(state.get("quality_retry_cap", QUALITY_RETRY_CAP))
    feedback = state.get("quality_check_feedback")

    if feedback and quality_retry_count < quality_retry_cap:
        return N_COMPREHENSION

    return N_REPORTER

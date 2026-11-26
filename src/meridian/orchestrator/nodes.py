"""LangGraph node entry points for the Meridian Testing Agent orchestrator.

Each node is a plain function ``(state: MeridianState) -> dict[str, Any]``.
It returns only the state fields it updates; LangGraph merges the result into
the shared state. Nodes do not call each other directly — routing is handled
by ``routing.py``.

LLM-dependent nodes (comprehension, generator, diagnosis) contain clearly
marked integration points. The LLM provider/model is not yet finalised, so
these nodes stub the LLM call and record a placeholder result. They are safe
to exercise without a live provider.

Deterministic nodes (test_runner_client, assertion_quality_check) call into
their respective modules, which are implemented separately.

See docs/architecture.md sections 3-7 and AGENTS.md sections 3-4.
"""

from __future__ import annotations

import time
from typing import Any

from meridian.orchestrator.state import (
    MeridianState,
    initial_state,
    STATUS_RUNNING,
    STATUS_AWAITING_APPROVAL,
    STATUS_DONE,
    STATUS_CAPPED,
    STATUS_REJECTED,
    RETRY_CAP,
    QUALITY_RETRY_CAP,
)

# ---------------------------------------------------------------------------
# Module execution budget (seconds). Enforced by the orchestrator across all
# stages. The test-runner timeout must be shorter than this.
# ---------------------------------------------------------------------------

MODULE_DEADLINE_SECONDS: float = 600.0      # 10 minutes (client constraint)
TEST_EXECUTION_TIMEOUT_SECONDS: float = 420.0  # 7 minutes (default, < deadline)


# ---------------------------------------------------------------------------
# Node 1 — Orchestrator
# ---------------------------------------------------------------------------

def orchestrator_node(state: MeridianState) -> dict[str, Any]:
    """Entry point for a module run.

    Initialises shared state, sets execution budgets and retry limits, starts
    the Langfuse trace, and records the start time. Routes to the Comprehension
    Agent.

    Returns a partial state update.
    """
    start = time.time()

    # (Re)initialise state if this is a fresh run. On resume from interrupt the
    # incoming state already has values; preserve them except the start marker.
    fresh = initial_state(state.get("module_name", ""), state.get("module_path", ""))

    return {
        "module_name": fresh["module_name"],
        "module_path": fresh["module_path"],
        "retry_cap": RETRY_CAP,
        "quality_retry_cap": QUALITY_RETRY_CAP,
        "status": STATUS_RUNNING,
        # execution_duration_seconds is accumulated by the reporter; start time
        # is recorded externally by the graph runner via langfuse.
        "_start_time": start,
    }


# ---------------------------------------------------------------------------
# Node 2 — Comprehension Agent
# ---------------------------------------------------------------------------

def comprehension_node(state: MeridianState) -> dict[str, Any]:
    """Reads and analyses the target module; produces a comprehension summary.

    Uses MCP read-only tools (read_file, list_symbols, read_docstrings) via
    src/meridian/agents/code_understanding.py. On Loop 2 re-entry, also
    incorporates quality_check_feedback from the Assertion Quality Check.

    LLM integration point: the comprehension summary is produced by an LLM
    call (temperature 0.2). Stubbed here until the provider is finalised.
    """
    module_path = state.get("module_path", "")
    feedback = state.get("quality_check_feedback")

    # TODO(LLM): replace stub with real comprehension call via code_understanding.py
    summary_parts = [f"Comprehension summary for module: {module_path}"]
    if feedback:
        summary_parts.append(f"Quality feedback to incorporate: {feedback}")
    summary_parts.append(
        "Public API, normal paths, boundaries, exceptions, and risky paths "
        "are documented here once the LLM provider is integrated."
    )
    comprehension_summary = "\n".join(summary_parts)

    return {
        "comprehension_summary": comprehension_summary,
        "status": STATUS_RUNNING,
    }


# ---------------------------------------------------------------------------
# Node 3 — Generator Agent
# ---------------------------------------------------------------------------

def generator_node(state: MeridianState) -> dict[str, Any]:
    """Generates pytest test cases from the comprehension summary.

    Input: comprehension summary (or diagnosis feedback if Loop 1 fired).
    Covers normal paths, boundaries, invalid inputs, exceptions, forgotten
    states, dependencies. Temperature 0.2.

    LLM integration point: test generation via an LLM call. Stubbed here.
    """
    summary = state.get("comprehension_summary", "")

    # TODO(LLM): replace stub with real test generation via test_generation.py
    generated_tests = [
        f"# Generated tests for {state.get('module_name', 'unknown_module')}\n"
        f"# Source comprehension summary:\n# {summary[:200]}\n"
        "# TODO: replace with real pytest tests once LLM provider is integrated.\n"
    ]

    return {
        "generated_tests": generated_tests,
        "status": STATUS_RUNNING,
    }


# ---------------------------------------------------------------------------
# Node 4 — Test Runner Client (deterministic, no LLM)
# ---------------------------------------------------------------------------

def test_runner_client_node(state: MeridianState) -> dict[str, Any]:
    """Sends generated tests to the isolated test-runner service via HTTP.

    Calls src/meridian/testing/test_runner_client.py. Applies a hard timeout
    (TEST_EXECUTION_TIMEOUT_SECONDS, default 7 minutes) per module. Stores
    per-test results, failures, and tracebacks in state.

    Does NOT execute pytest in the main application process.
    """
    tests = state.get("generated_tests", [])
    module_name = state.get("module_name", "unknown")

    # TODO: wire to test_runner_client.execute_tests(tests, module_name, timeout=...)
    # Once Docker/DinD is available (currently blocked — see B1 in
    # docs/requirements-traceability.md), this node performs the real HTTP call.
    test_results = [
        {
            "name": f"{module_name}_placeholder_test",
            "passed": None,
            "traceback": None,
            "note": "test-runner client not yet wired; Docker/DinD unavailable (blocker B1)",
        }
    ]

    return {
        "test_results": test_results,
        "status": STATUS_RUNNING,
    }


# ---------------------------------------------------------------------------
# Node 5 — Diagnosis Agent
# ---------------------------------------------------------------------------

def diagnosis_node(state: MeridianState) -> dict[str, Any]:
    """Analyses failed test results and decides: bad test or likely defect.

    Distinguishes incorrect generated tests / assumptions / import problems /
    environment failures from genuine production-code defects. Invalid tests go
    back to the Generator (Loop 1, increment retry_count). Genuine defects are
    recorded in bug_findings. Never classifies every failure as a production bug.

    LLM integration point: diagnosis reasoning via an LLM call (temperature 0.2).
    Stubbed here.
    """
    test_results = state.get("test_results", [])
    retry_count = state.get("retry_count", 0)
    retry_cap = state.get("retry_cap", RETRY_CAP)

    # TODO(LLM): replace stub with real diagnosis via failure_diagnosis.py
    # The stub assumes all results are placeholders (no real execution yet),
    # so it takes neither loop branch and continues to quality check.
    # When a real bad-test decision is made, increment retry_count here so the
    # routing function can read the updated value.
    bug_findings = list(state.get("bug_findings", []))
    retry_count = int(state.get("retry_count", 0))
    decision = "continue_to_quality"  # no failures to diagnose yet

    return {
        "bug_findings": bug_findings,
        "retry_count": retry_count,
        "_diagnosis_decision": decision,
        "status": STATUS_RUNNING,
    }


# ---------------------------------------------------------------------------
# Node 6 — Assertion Quality Check (deterministic, no LLM)
# ---------------------------------------------------------------------------

def assertion_quality_check_node(state: MeridianState) -> dict[str, Any]:
    """Deterministically inspects generated test assertions.

    Detects empty test bodies, meaningless assertions (e.g. assert True), and
    tests that pass without verifying behaviour. Returns actionable feedback.
    Weak assertions route to Loop 2 (Comprehension Agent). Strong assertions
    continue to the Reporter.

    Implementation lives in src/meridian/testing/assertion_checker.py.
    """
    tests = state.get("generated_tests", [])
    quality_retry_count = int(state.get("quality_retry_count", 0))
    quality_retry_cap = int(state.get("quality_retry_cap", QUALITY_RETRY_CAP))

    # TODO: wire to assertion_checker.check(tests). The stub treats placeholder
    # tests as weak (they assert nothing meaningful), which would trigger Loop 2
    # once real tests are generated.
    weak = True  # placeholder tests have no real assertions
    feedback = None

    if weak:
        if quality_retry_count < quality_retry_cap:
            feedback = (
                "Generated tests passed but assert nothing meaningful. "
                "Re-read the module and regenerate with specific expected values "
                "for normal paths, boundaries, and error cases."
            )
            # Increment so the routing function can read the updated value.
            quality_retry_count += 1
        else:
            feedback = None  # quality cap reached; proceed to reporter as-is

    return {
        "quality_check_feedback": feedback,
        "quality_retry_count": quality_retry_count,
        "status": STATUS_RUNNING,
    }


# ---------------------------------------------------------------------------
# Node 7 — Reporter
# ---------------------------------------------------------------------------

def reporter_node(state: MeridianState) -> dict[str, Any]:
    """Assembles the final test file and module execution report.

    Outputs:
      reports/generated/<module_name>_tests.py
      reports/generated/<module_name>_report.md

    The report includes: test file, bug findings, retry count, token cost,
    execution duration, quality-check results, and mutation testing results
    (when available). Clearly distinguishes confirmed execution results from
    AI-generated suspected defects.
    """
    end = time.time()
    start = state.get("_start_time", end)
    duration = end - start
    module_name = state.get("module_name", "unknown_module")
    retry_count = state.get("retry_count", 0)
    token_cost = state.get("token_cost_usd", 0.0)
    bug_findings = state.get("bug_findings", [])
    quality_feedback = state.get("quality_check_feedback")

    report_lines = [
        f"# Meridian Execution Report — {module_name}",
        f"Status: {state.get('status')}",
        f"Retry count (Loop 1): {retry_count}",
        f"Quality retry count (Loop 2): {state.get('quality_retry_count', 0)}",
        f"Token cost (USD): {token_cost:.6f}",
        f"Execution duration (seconds): {duration:.2f}",
        f"Bug findings: {len(bug_findings)}",
        f"Quality check feedback: {quality_feedback or 'none'}",
        "",
        "## Bug Findings",
    ]
    if bug_findings:
        for bf in bug_findings:
            report_lines.append(f"- {bf}")
    else:
        report_lines.append("- None recorded.")

    report_lines += [
        "",
        "## Notes",
        "Confirmed execution results are distinguished from AI-generated suspected "
        "defects. No production code was modified.",
    ]

    report_md = "\n".join(report_lines)

    return {
        "execution_duration_seconds": duration,
        "report_md": report_md,
        "status": STATUS_AWAITING_APPROVAL,
    }


# ---------------------------------------------------------------------------
# Node 8 — Human Approval Gate
# ---------------------------------------------------------------------------

def human_approval_node(state: MeridianState) -> dict[str, Any]:
    """Pauses the graph for engineer approval via LangGraph interrupt().

    The engineer reviews the generated test file, execution report, bug
    findings, mutation results (when available), retry count, token cost, and
    duration. Decision: approve / edit and approve / reject.

    The actual interrupt() is implemented in approval.py; this node is the
    graph entry point that approval.wrap() decorates.
    """
    # The interrupt happens inside approval.human_approval_node (wrapped).
    # This placeholder returns no state change; approval.py owns the pause.
    return {"status": state.get("status", STATUS_AWAITING_APPROVAL)}

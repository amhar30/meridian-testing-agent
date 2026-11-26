"""Shared LangGraph state for the Meridian Testing Agent.

Defines the MeridianState TypedDict that is threaded through every node of
the eight-node graph, plus helper constructors and status/retry constants.

See docs/architecture.md section 6 and AGENTS.md section 6.
"""

from typing import TypedDict


# --- Retry / budget constants (Loop 1 and Loop 2 caps, tracked separately) ---

RETRY_CAP: int = 5          # Loop 1: diagnosis -> generator refinement cycles
QUALITY_RETRY_CAP: int = 3  # Loop 2: assertion quality -> comprehension cycles
TEST_EXECUTION_TIMEOUT_SECONDS: float = 420.0  # 7 minutes (default, < overall deadline)

# --- Status values ---

STATUS_RUNNING = "running"
STATUS_AWAITING_APPROVAL = "awaiting_approval"
STATUS_DONE = "done"
STATUS_CAPPED = "capped"
STATUS_REJECTED = "rejected"


# --- TypedDict for shared state ---

class MeridianState(TypedDict):
    """Shared state passed between all LangGraph nodes."""

    # Module identification
    module_name: str
    module_path: str

    # Comprehension / generation artifacts
    comprehension_summary: str
    generated_tests: list[str]

    # Execution results
    test_results: list[dict]      # per-test: name, passed, traceback
    bug_findings: list[str]

    # Loop 1: diagnosis -> generator refinement (capped at 5)
    retry_count: int
    retry_cap: int

    # Loop 2: assertion quality -> comprehension (capped at 3, independent of Loop 1)
    quality_retry_count: int
    quality_retry_cap: int

    # Cost / timing
    token_cost_usd: float
    execution_duration_seconds: float

    # Human approval gate (LangGraph interrupt)
    approval_decision: str | None   # "approved" | "rejected" | None
    approval_feedback: str | None

    # Observability
    langfuse_trace_id: str
    quality_check_feedback: str | None

    # Lifecycle
    status: str  # "running" | "awaiting_approval" | "done" | "capped" | "rejected"


def initial_state(module_name: str, module_path: str) -> MeridianState:
    """Create a fresh MeridianState for a new module run."""
    return MeridianState(
        module_name=module_name,
        module_path=module_path,
        comprehension_summary="",
        generated_tests=[],
        test_results=[],
        bug_findings=[],
        retry_count=0,
        retry_cap=RETRY_CAP,
        quality_retry_count=0,
        quality_retry_cap=QUALITY_RETRY_CAP,
        token_cost_usd=0.0,
        execution_duration_seconds=0.0,
        approval_decision=None,
        approval_feedback=None,
        langfuse_trace_id="",
        quality_check_feedback=None,
        report_md=None,
        status=STATUS_RUNNING,
    )
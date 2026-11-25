# Meridian Testing Agent — Architecture

**Project:** Meridian Systems Regression Safety Net  
**Stack decision date:** November 2026  
**Author:** Group 04

---

## 1. System Overview

Meridian Testing Agent is a multi-agent AI system built on LangGraph. It reads an unfamiliar Python module, generates meaningful pytest tests, executes them in an isolated Docker container, refines them through feedback loops, and hands an engineer a reviewable test file.

**The primary metric is mutation catch rate — not coverage percentage.**

---

## 2. Non-Negotiable Stack

| Area | Technology | Reason |
|---|---|---|
| Orchestration | LangGraph StateGraph | Required by engineering standards |
| Observability | Langfuse | Required by engineering standards |
| Tool access | MCP server (read-only) | Required by engineering standards |
| Working memory | LangGraph state (TypedDict) | Required by engineering standards |
| Long-term memory | SQLite | Lightweight, no external service needed |
| Test execution | Isolated Docker container | Client requires no production access |
| Test framework | pytest + pytest-json-report | Structured JSON output for Diagnosis Agent |
| Mutation testing | mutmut | Client's stated evaluation method |
| API | FastAPI | Test runner endpoint + main app |
| Human approval | LangGraph interrupt() | Client requires engineer approval before merge |
| LLM temperature | 0.2 | Client requires deterministic output |
| Containerisation | Docker Compose | Required by engineering standards |

---

## 3. Eight-Node LangGraph Graph

```
Orchestrator
    ↓
Comprehension Agent  ←─────────────────────────────┐
    ↓                                               │
Generator Agent  ←──────────────────┐              │
    ↓                               │              │
Test Runner (Docker)                │              │
    ↓                               │              │
Diagnosis Agent ────── bad test ────┘ (Loop 1)     │
    ↓ real bug or cap reached                       │
Assertion Quality Check ── weak assertion ──────────┘ (Loop 2)
    ↓ all assertions meaningful
Reporter
    ↓
Human Approval Gate (LangGraph interrupt)
    ↓ approved
Done → next module
```

---

## 4. Agent Responsibilities

### Node 1 — Orchestrator
- Entry point for each module run
- Sets retry cap (default 5) and quality retry cap (default 3)
- Initialises Langfuse trace
- Routes to Comprehension Agent to begin
- After Reporter, loops to next module or exits
- File: `src/meridian/orchestrator/graph.py` + `nodes.py`

### Node 2 — Comprehension Agent
- Reads module via MCP tools: `read_file`, `list_symbols`, `read_docstrings`
- Produces structured summary: public API, normal paths, boundaries, exceptions, risky paths
- Also receives quality-check feedback when Loop 2 fires
- File: `src/meridian/agents/code_understanding.py`

### Node 3 — Generator Agent
- Input: comprehension summary (or diagnosis feedback if Loop 1)
- Generates pytest test cases covering: normal paths, boundaries, errors, forgotten states
- Temperature: 0.2
- File: `src/meridian/agents/test_generation.py`

### Node 4 — Test Runner Client
- Deterministic node — no LLM
- Sends test code to isolated Docker container via HTTP POST
- Timeout: configurable, must be shorter than overall 10-minute module deadline
- Returns per-test pass/fail/traceback to LangGraph state
- File: `src/meridian/testing/test_runner_client.py`

### Node 5 — Diagnosis Agent
- Receives: test results + original module code
- Decides per failure: bad test OR real bug
- Bad test → Loop 1 back to Generator (increment retry_count)
- Real bug → add to bug_findings, continue
- If retry_cap reached → mark module as partially covered, continue
- File: `src/meridian/agents/failure_diagnosis.py`

### Node 6 — Assertion Quality Check
- Deterministic node — no LLM
- Checks the strength and relevance of assertions, not merely whether an assertion exists
- Rejects: `assert True`, empty test body, assertions that cannot distinguish correct from incorrect behaviour
- Context-aware: `assert result is not None` may be meaningful depending on the function — do not reject automatically
- Weak assertions → Loop 2 back to Comprehension Agent with specific feedback
- All pass → continue to Reporter
- File: `src/meridian/testing/assertion_checker.py`

### Node 7 — Reporter
- Assembles: final test file, coverage note, bug findings, retry count, token cost, duration
- Output: `reports/generated/<module_name>_tests.py` and `<module_name>_report.md`
- File: `src/meridian/agents/report_generation.py`

### Node 8 — Human Approval Gate
- LangGraph `interrupt()` — graph pauses here
- Engineer reviews: test file, report, bug list, cost, retry count
- Decisions: approve / edit and approve / reject
- Nothing merges without approval
- File: `src/meridian/orchestrator/approval.py`

---

## 5. Two Feedback Loops

### Loop 1: Diagnosis Agent → Generator Agent
- **Condition:** test is wrong (bad assumption, import error, type mismatch) — not a real bug
- **Flow:** Diagnosis → Generator → Test Runner → Diagnosis
- **Limit:** retry_count max 5 (tracked separately per module)
- **On cap reached:** mark module partially covered, continue to quality check

### Loop 2: Assertion Quality Check → Comprehension Agent
- **Condition:** test passes but asserts nothing meaningful
- **Flow:** Quality Check → Comprehension → Generator → Test Runner
- **Feedback message:** "tests passed but assert nothing; re-read the module and regenerate with specific expected values"
- **Limit:** quality_retry_count max 3 (tracked separately from Loop 1)

Both loop counters are tracked independently in LangGraph state.

---

## 6. Shared LangGraph State

File: `src/meridian/orchestrator/state.py`

```python
from typing import TypedDict


class MeridianState(TypedDict):
    module_name: str
    module_path: str

    comprehension_summary: str
    generated_tests: list[str]

    test_results: list[dict]       # per-test: name, passed, traceback
    bug_findings: list[str]

    retry_count: int               # Loop 1 counter
    retry_cap: int                 # default 5

    quality_retry_count: int       # Loop 2 counter
    quality_retry_cap: int         # default 3

    token_cost_usd: float
    execution_duration_seconds: float

    approval_decision: str | None  # "approved" | "rejected" | None
    approval_feedback: str | None

    langfuse_trace_id: str
    quality_check_feedback: str | None

    status: str  # "running" | "awaiting_approval" | "done" | "capped" | "rejected"
```

---

## 7. Docker Architecture

Four containers in `docker-compose.yml` at project root:

| Container | Contents | Access |
|---|---|---|
| `app` | FastAPI + LangGraph orchestrator + all agents | Internal only |
| `test-runner` | Minimal Python image; POST /run-tests; runs pytest in subprocess | No internet, no repo writes, no LLM keys |
| `langfuse` | Official Langfuse image for local tracing | Internal only |
| `mcp-server` | FastAPI MCP; read-only repo volume mount | Read-only filesystem |

### Test Runner Client vs Server

These are separate components:

- `src/meridian/testing/test_runner_client.py`
  - Runs in the main application container
  - Sends HTTP POST requests to the test-runner service
  - Receives structured JSON results
  - Does not execute pytest locally

- `src/meridian/test_runner/server.py`
  - Runs inside the test-runner service container
  - Receives and validates HTTP requests
  - Coordinates isolated test execution
  - Returns structured JSON results
  - Must not execute untrusted test code inside its own server process

- `src/meridian/test_runner/runner.py`
  - Coordinates actual pytest execution in a separately restricted environment
  - Prepares temporary workspace
  - Launches pytest as a separate subprocess with restricted permissions (not inside the HTTP server process)
  - A subprocess alone is not a sufficient security boundary — apply resource limits, restricted filesystem, and no network access at the process level
  - Returns structured results to server

### Execution Timeouts

- Overall module execution deadline: 10 minutes (enforced by Orchestrator)
- Test execution timeout: configurable, must be shorter than overall deadline (default 7 minutes)
- Remaining time after test execution is reserved for Diagnosis, Quality Check, and Reporter
- The Orchestrator enforces the overall deadline across all workflow stages

### Test Runner Security Boundaries
- No internet access
- No production credentials
- No LLM API keys
- No Docker socket
- No privileged mode
- Read-only access to required source and dependency files
- Writable temporary storage under /tmp only
- No access to unrelated host files or application secrets
- The original repository is never writable by the test runner
- CPU, memory and time limits enforced
- Structured output validation on responses

---

## 8. Mutation Testing

Tool: `mutmut`  
Script: `scripts/run_evaluation.py`  
Results: `evaluation/evaluation_results/`

### Process
1. Copy target module to isolated temp directory
2. Run: `mutmut run --paths-to-mutate <temp_copy>`
3. For each surviving mutant: record which test missed it
4. Score = `killed_mutants / executable_mutants × 100`
5. Write: `evaluation/evaluation_results/<module_name>_eval.json`

### Mutation Score Definition
```
Mutation Catch Rate = (Killed Mutants / Executable Mutants) × 100
```

The denominator is **executable mutants only** — not total mutants generated.

Report separately:
- Killed mutants (caught by tests)
- Surviving mutants (missed by tests)
- Equivalent mutants (semantically identical to original — excluded from score)
- Failed-to-execute mutants (syntax errors, timeouts — excluded from score, reported transparently)

### Rules
- Never mutate the original production module
- Run in isolated temp workspace
- Do not report a misleading score when mutants could not execute
- Always state how many mutants were excluded and why

---

## 9. Langfuse Observability

File: `src/meridian/observability/langfuse_client.py`

- One trace per module run: `module_run_{module_name}_{timestamp}`
- One span per node: `comprehension`, `generation`, `test_execution`, `diagnosis`, `quality_check`, `mutation_testing`, `report`, `human_approval`
- Each span records: input_tokens, output_tokens, cost_usd, latency_ms, retry_count
- Deterministic nodes record latency only — no invented token usage

---

## 10. Memory Architecture

| Layer | File | Contents |
|---|---|---|
| Working memory | LangGraph state | Active module execution context |
| Long-term memory | `memory/sqlite_store.py` | Past module results, confirmed conventions, approved test outcomes |
| Checkpointing | `memory/checkpointing.py` | LangGraph SqliteSaver for interrupt/resume |

SQLite is the only database. No Supabase. No PostgreSQL.

### Three Separate Memory Responsibilities

Keep these separate in implementation, even if they share one SQLite database file:

| Responsibility | File | Contents |
|---|---|---|
| Working memory | LangGraph state (in-memory) | Current module execution data — lost when graph ends |
| Long-term memory | `memory/sqlite_store.py` | Previously confirmed conventions, useful historical results, approved test outcomes |
| Checkpointing | `memory/checkpointing.py` | Graph execution progress — allows interrupted approval workflow to resume |

These are related but distinct. Do not assume they are interchangeable.

### LangGraph Checkpointing Requirements
- Use a persistent SQLite-backed LangGraph checkpointer (SqliteSaver or AsyncSqliteSaver)
- Preserve the same `thread_id` when resuming an interrupted graph
- Approval state must survive application restarts
- Select synchronous or asynchronous checkpointing according to the graph execution model
- Checkpointing is required for the Human Approval Gate interrupt to work correctly

---

## 11. MCP Server Tools

File: `src/meridian/mcp/server.py`

| Tool | Description |
|---|---|
| `read_file(path)` | Read a source file from the target repo |
| `list_symbols(path)` | List functions, classes, imports in a module |
| `read_docstrings(path)` | Extract all docstrings from a module |

All tools are read-only. No writes to the repository. Path traversal prevention enforced.

---

## 12. Cost Model (required deliverable)

Unit: one module covered (from first comprehension call to approved test file)

| Line item | Driver |
|---|---|
| Comprehension tokens | Module size in tokens |
| Generation tokens | Attempts per module |
| Diagnosis tokens | Failures × refinement cycles |
| Test execution compute | Runs × refinement cycles |
| CI integration | Per pull request on covered modules |
| Observability | Spans per module run |
| Engineer time displaced | Assumed $80/hr, 2hrs manual per module |

Report must include:
- Cost per one module covered
- Monthly cost at normal volume (20 modules/day × 22 working days)
- Monthly cost at peak volume (60 modules/day × 22 working days)
- Break-even vs engineer time
- Every unit price with source URL and date looked up
- Actual API expenditure separated from estimated engineer time savings
- Working days assumption stated explicitly (default: 22 days/month)

---

## 13. What is Out of Scope

- Voice or audio interface
- Writing or refactoring production code
- General-purpose tool building
- Production database access
- Supabase or PostgreSQL
- Autonomous merges without engineer approval

---

## 14. Stable Reruns — Reproducibility Record

Temperature 0.2 reduces variance but does not guarantee identical output. For each evaluation run, record:

| Field | Example |
|---|---|
| Model provider | openai |
| Model identifier | gpt-4o-2024-11-20 |
| Temperature | 0.2 |
| Prompt version | v1.2 |
| Source repo commit SHA | a3f9c12 |
| Python version | 3.11.9 |
| Container image digest | sha256:abc123... |
| Test runner config hash | sha256 of benchmark_config.yaml |
| Dependency versions | sha256 of requirements.txt |
| Generated test file hash | sha256 of output file |
| mutmut config version | benchmark_config.yaml hash |

Store this record alongside each evaluation result in `evaluation/evaluation_results/`.

---

## 15. Definition of Done

1. Twenty named modules covered by engineer-reviewed and merged tests
2. Mutation catch rate reported
3. Zero tests pass while asserting nothing meaningful
4. Re-running on unchanged code produces stable comparable tests
5. Under 10 minutes wall clock per module
6. Cost per module with average retry count shown
7. Human approval enforced before any merge
8. Reproducible from a clean machine via Docker Compose
9. Langfuse traces cover every module run

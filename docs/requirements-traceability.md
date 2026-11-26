# Meridian Testing Agent — Requirements Traceability

**Status:** Draft — Milestone 1  
**Owner:** Architect (integration & traceability)  
**Source requirements:** docs/client-brief.md, docs/project-brief.md, docs/architecture.md, AGENTS.md

## Traceability Conventions

Each requirement is mapped to:
- **Component(s):** source files responsible
- **Verification:** how compliance is proven (test, demo, artifact, or runtime evidence)
- **Status:** IMPLEMENTED / PARTIAL / NOT_STARTED / BLOCKED

A requirement with no artifact is not considered met (per project-brief §02: "No artifact, no mark").

---

## 1. Client Requirements (client-brief.md)

| # | Requirement (brief ref) | Component(s) | Verification | Status |
|---|-------------------------|--------------|--------------|--------|
| C1 | Read an unfamiliar Python module and determine intended behaviour | `src/meridian/agents/code_understanding.py`, `src/meridian/mcp/` | Generated comprehension summary for a real module | NOT_STARTED |
| C2 | Generate pytest tests covering normal paths, boundaries, errors, forgotten states | `src/meridian/agents/test_generation.py` | Reviewable test file produced in `reports/generated/` | NOT_STARTED |
| C3 | Execute generated tests in isolated Docker environment | `src/meridian/testing/test_runner_client.py`, `src/meridian/test_runner/` | Successful pytest run in container, JSON results returned | BLOCKED — DinD unavailable (see §6) |
| C4 | Diagnose failures: distinguish bad test from likely production defect | `src/meridian/agents/failure_diagnosis.py` | Diagnosis decision recorded in state + bug_findings | NOT_STARTED |
| C5 | Refine wrong tests via bounded feedback loops; report likely bugs | `src/meridian/orchestrator/routing.py`, `src/meridian/agents/failure_diagnosis.py` | Loop 1 terminates at retry_cap; bug_findings populated | NOT_STARTED |
| C6 | Hand engineer a reviewable test file + note on coverage/exclusions | `src/meridian/agents/report_generation.py` | `reports/generated/<module>_tests.py` and `_report.md` exist | NOT_STARTED |
| C7 | No generated test merged without engineer approval | `src/meridian/orchestrator/approval.py` | Graph pauses at interrupt; decision recorded before merge | NOT_STARTED |
| C8 | Determinism: re-running on unchanged code yields stable, comparable tests | All agent nodes | Same input → same output across runs (temperature 0.2) | NOT_STARTED |
| C9 | Mutation catch rate reported (seeded bugs), not coverage % | `scripts/run_evaluation.py`, `src/meridian/testing/mutation_testing.py` | `evaluation/evaluation_results/<module>_eval.json` with killed/surviving counts | NOT_STARTED |
| C10 | Under 10 minutes wall clock per module | Orchestrator + test-runner | Measured execution_duration_seconds < 600s | NOT_STARTED |
| C11 | Cost per module + average retry count reported | Reporter + Langfuse | `reports/generated/<module>_report.md` includes cost + retry_count | NOT_STARTED |
| C12 | No production access; system reads repo only | MCP server (read-only), security/ | MCP tools are read-only; no write paths exposed | NOT_STARTED |

---

## 2. Engineering Standards (AGENTS.md §2, project-brief.md DOC-B)

| # | Requirement | Component(s) | Verification | Status |
|---|-------------|--------------|--------------|--------|
| E1 | LangGraph StateGraph orchestration | `src/meridian/orchestrator/graph.py` | Graph compiles; 8 nodes present | NOT_STARTED |
| E2 | Shared state = Python TypedDict | `src/meridian/orchestrator/state.py` | `MeridianState` TypedDict defined with all fields | NOT_STARTED |
| E3 | Human approval via LangGraph `interrupt()` | `src/meridian/orchestrator/approval.py` | `interrupt()` called before merge gate | NOT_STARTED |
| E4 | LLM configurable via env vars; temperature 0.2 for gen/diagnosis | `src/meridian/config/settings.py`, agent nodes | Model identifier sourced from env; temperature hard-coded 0.2 | NOT_STARTED |
| E5 | FastAPI | `src/meridian/interfaces/web.py`, `src/meridian/test_runner/server.py` | HTTP endpoints respond | NOT_STARTED |
| E6 | Langfuse observability | `src/meridian/observability/langfuse_client.py` | One trace per module run; spans per node | NOT_STARTED |
| E7 | pytest + pytest-json-report | `src/meridian/test_runner/runner.py` | Structured JSON test results | NOT_STARTED |
| E8 | Isolated Docker test execution | `src/meridian/test_runner/`, `docker-compose.yml` | Child containers isolated, no network, resource limits | BLOCKED — DinD unavailable |
| E9 | Python AST code analysis | `src/meridian/analysis/ast_analyzer.py` | AST-based symbol extraction works | NOT_STARTED |
| E10 | MCP tool integration (read-only) | `src/meridian/mcp/server.py` | `read_file`, `list_symbols`, `read_docstrings` exposed | NOT_STARTED |
| E11 | Working memory = LangGraph state | `src/meridian/orchestrator/state.py` | Active execution context in TypedDict | NOT_STARTED |
| E12 | Long-term memory = SQLite | `src/meridian/memory/sqlite_store.py` | SQLite DB stores historical module info | NOT_STARTED |
| E13 | Docker Compose orchestration | `docker-compose.yml` | `docker compose up` starts services | BLOCKED — Docker unavailable |
| E14 | GitHub Actions CI/CD | `infrastructure/github/workflows/regression-tests.yml` | Workflow runs on PR | NOT_STARTED |
| E15 | mutmut mutation testing | `scripts/run_evaluation.py` | mutmut runs on isolated copy; results recorded | NOT_STARTED |

---

## 3. Architecture Constraints (architecture.md)

| # | Constraint | Component(s) | Verification | Status |
|---|------------|--------------|--------------|--------|
| A1 | Exactly 8 LangGraph nodes | `src/meridian/orchestrator/graph.py` | Node count == 8 | NOT_STARTED |
| A2 | Exactly 2 bounded feedback loops | `src/meridian/orchestrator/routing.py` | Loop 1 (retry_count) + Loop 2 (quality_retry_count) | NOT_STARTED |
| A3 | Loop 1 retry_count max 5 | `src/meridian/orchestrator/routing.py` | Cap enforced; module marked capped at limit | NOT_STARTED |
| A4 | Loop 2 quality_retry_count max 3 | `src/meridian/orchestrator/routing.py` | Cap enforced separately from Loop 1 | NOT_STARTED |
| A5 | mutation_testing is a Langfuse span, not a graph node | `src/meridian/observability/`, `scripts/run_evaluation.py` | No 9th node; mutation appears as span only | NOT_STARTED |
| A6 | Human approval mandatory before merge; no autonomous merge | `src/meridian/orchestrator/approval.py` | interrupt() blocks; resume requires explicit decision | NOT_STARTED |
| A7 | Architecture changes require new ADR before code | `docs/adr/` | Any change has matching ADR | NOT_STARTED |
| A8 | No Supabase/PostgreSQL for Meridian memory | `src/meridian/memory/` | SQLite only | NOT_STARTED |
| A9 | No voice components | — | No voice code | NOT_STARTED |
| A10 | Working memory in LangGraph state | `src/meridian/orchestrator/state.py` | Active context in TypedDict | NOT_STARTED |
| A11 | Long-term memory via SQLite `memory/sqlite_store.py` | `src/meridian/memory/sqlite_store.py` | Separate from checkpointing | NOT_STARTED |
| A12 | Persistent checkpointing via SQLite `memory/checkpointing.py` | `src/meridian/memory/checkpointing.py` | Separate from long-term memory | NOT_STARTED |
| A13 | LangGraph interrupt() + persistent checkpointer for resume | `src/meridian/orchestrator/approval.py`, `memory/checkpointing.py` | interrupt/resume with same thread_id works | NOT_STARTED |
| A14 | Each ADR: context, decision, alternatives, rejection reasons, consequences, status | `docs/adr/` | ADR template followed | NOT_STARTED |
| A15 | Rejected alternatives recorded with reason | `docs/adr/` | Every ADR lists rejected options | NOT_STARTED |

---

## 4. Orchestrator-Specific (AGENTS.md §3.1, §4, §5, §6, §7)

| # | Requirement | Component(s) | Verification | Status |
|---|-------------|--------------|--------------|--------|
| O1 | Start module execution; initialize shared state | `nodes.py`, `graph.py` | Orchestrator node sets initial state | NOT_STARTED |
| O2 | Set execution budgets and retry limits | `nodes.py` | retry_cap, quality_retry_cap initialized | NOT_STARTED |
| O3 | Route through required agent nodes in order | `graph.py`, `routing.py` | Comprehension → Generation → Test Execution → Diagnosis → Quality Check → Reporter → Approval | NOT_STARTED |
| O4 | Track execution status | `state.py` (`status` field) | Status transitions: running → awaiting_approval → done/capped/rejected | NOT_STARTED |
| O5 | Handle both feedback loops | `routing.py` | Loop 1 and Loop 2 conditional edges present | NOT_STARTED |
| O6 | Pause for human approval before merge | `approval.py` | interrupt() at approval gate | NOT_STARTED |
| O7 | Resume/reject based on engineer decision | `approval.py`, `routing.py` | Decision changes status; rejected tests don't merge | NOT_STARTED |
| O8 | Continue to next module when done/rejected | `nodes.py` | Graph exits or routes to next module | NOT_STARTED |
| O9 | 10-minute module execution deadline | `nodes.py`, `settings.py` | deadline enforced across all stages | NOT_STARTED |
| O10 | Test execution timeout shorter than deadline (default 7 min) | `test_runner_client.py`, `settings.py` | timeout < 600s | NOT_STARTED |

---

## 5. Observability (architecture.md §9, AGENTS.md §10)

| # | Requirement | Component(s) | Verification | Status |
|---|-------------|--------------|--------------|--------|
| L1 | One trace per module run | `langfuse_client.py` | trace_id per module | NOT_STARTED |
| L2 | One span per node (comprehension, generation, test_execution, diagnosis, quality_check, mutation_testing, report, human_approval) | `langfuse_client.py`, tracing.py | 8 spans per trace | NOT_STARTED |
| L3 | Track LLM input/output tokens and cost USD | `langfuse_client.py` | token_cost_usd recorded | NOT_STARTED |
| L4 | Deterministic nodes record latency only (no invented tokens) | `langfuse_client.py` | Latency spans without token data for deterministic nodes | NOT_STARTED |
| L5 | Track retries, errors, failures, approval outcomes | `langfuse_client.py` | retry_count, error spans, approval decision spans | NOT_STARTED |

---

## 6. Known Blockers & Open Decisions

| ID | Blocker / Decision | Impact | Required Action |
|----|--------------------|--------|-----------------|
| B1 | **Docker/DinD unavailable in this WSL2 environment.** No `dockerd`, no socket, Docker Desktop daemon unreachable from WSL. | Test execution (C3, E8, E13) cannot run; `docker-compose.yml` cannot be validated locally. | Per ADR-001 §"If DinD Is Unavailable": work on sandbox/test-runner stops pending architect-approved alternative. Do NOT introduce host socket or unrestricted subprocess. Owner must approve alternative or confirm environment will provide Docker. |
| D1 | LLM provider/model identifier not yet finalised. | Agent nodes (comprehension, generation, diagnosis) cannot make real LLM calls. | Owner indicated provider/model decision is being finalised. Build non-LLM-dependent components (state, graph, routing, approval, deterministic checkers) in parallel. |
| D2 | Twenty target modules not yet selected. | Golden-path module choice pending. | Testing Engineer to identify one real Python module for Milestone 1 golden path. |

---

## 7. Milestone 1 — LangGraph Orchestrator (Current Focus)

| File | Requirement coverage | Status |
|------|---------------------|--------|
| `src/meridian/orchestrator/state.py` | E2, A10, O4, MeridianState TypedDict | IN_PROGRESS |
| `src/meridian/orchestrator/graph.py` | E1, A1, O3, 8-node graph | PENDING |
| `src/meridian/orchestrator/routing.py` | A2, A3, A4, O5, O6, both feedback loops | PENDING |
| `src/meridian/orchestrator/approval.py` | E3, A6, A13, O6, O7 | PENDING |
| `src/meridian/orchestrator/nodes.py` | O1, O2, O8, O9 | PENDING |

---

**Next verification step:** After `state.py` is implemented, run a Python import/type check to confirm `MeridianState` is well-formed, then proceed to `graph.py`.

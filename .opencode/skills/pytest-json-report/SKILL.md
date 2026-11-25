---
name: pytest-json-report
description: Use when wiring Meridian test-runner pytest output, parsing --json-report results, or debugging structured per-test results.
---

# pytest-json-report in Meridian

Read docs/architecture.md §2 and §7 before changing runner output.

## Use
- Required plugin for structured test results (`pytest-json-report`).
- Invoke pytest in the restricted subprocess in `src/meridian/test_runner/runner.py` with a JSON report file in the temp workspace.
- Parse per-test nodeid, outcome, duration, traceback/error text, and collection/import errors.
- Return validated JSON to `server.py`, then to `test_runner_client.py` and LangGraph state.
- Preserve distinct outcomes for pass, fail, error, skip, and collection failure; do not collapse errors into failures.
- Keep raw tracebacks out of user-facing reports unless needed; store structured summaries.

## Rules
- Never execute pytest in the FastAPI server process.
- Write reports only to the temporary writable workspace; clean up afterward.
- Treat missing/partial JSON (timeouts, crashes) as an explicit execution error, not a pass.
- Validate and bound response fields before updating `MeridianState.test_results`.
- Do not invent token or cost data; this is deterministic execution metadata.
- Pin the plugin version in test-runner requirements for reproducibility.

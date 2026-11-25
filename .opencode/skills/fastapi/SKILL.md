---
name: fastapi
description: Use when implementing Meridian FastAPI endpoints in src/meridian/interfaces/web.py or the test-runner server src/meridian/test_runner/server.py.
---

# FastAPI in Meridian

Read AGENTS.md §3.5-3.6 and docs/architecture.md §7 before editing APIs.

## Endpoints
- Main app API lives in `src/meridian/interfaces/web.py`.
- Test-runner service exposes `POST /run-tests` in `src/meridian/test_runner/server.py`.
- Use Pydantic request/response models; reject malformed test code and paths with 4xx and structured errors.
- Include health/readiness endpoints for Compose and CI checks.

## Rules
- The test-runner HTTP process must never execute submitted pytest code itself; delegate to `runner.py`.
- Authenticate requests between `app` and `test-runner`; load secrets from settings/env, never hardcode.
- Apply request size, concurrency, and time limits; return clear 4xx/5xx errors without tracebacks.
- Do not log secrets, credentials, or full untrusted source by default.
- Keep deterministic endpoints free of LLM calls and token/cost claims.
- Use async handlers only for I/O; bound blocking work and run test execution out-of-process.
- Keep response schemas stable for `test_runner_client.py` and LangGraph state updates.

## Verify
- Add tests under `tests/integration/` and `tests/security/` for validation, auth, timeout, and malformed input.

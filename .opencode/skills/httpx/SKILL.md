---
name: httpx
description: Use when implementing Meridian's test-runner HTTP client in src/meridian/testing/test_runner_client.py or calling FastAPI services with httpx.
---

# httpx in Meridian

Read AGENTS.md §3.4 and docs/architecture.md §7 before editing the client.

## Client
- `test_runner_client.py` runs in the app container and calls `POST /run-tests` over HTTP.
- Never execute generated pytest in the app process; the client only sends/receives JSON.
- Use `httpx.Client` or `AsyncClient` consistently with the graph; close clients cleanly.
- Set explicit connect/read/write timeouts shorter than the 10-minute module deadline.
- Test execution timeout defaults to 7 minutes; leave time for diagnosis, quality check, and reporting.
- Include authentication headers sourced from settings; never hardcode or log secrets.

## Handling
- Treat timeouts, connection errors, non-2xx responses, and invalid JSON as structured failures in state.
- Validate response schema and bound per-test fields before updating `MeridianState.test_results`.
- Do not blindly retry test execution; respect loop caps and avoid duplicate costs.
- Preserve service error details for diagnosis without leaking secrets.

## Verify
- Add tests for timeout, malformed response, service unavailable, and auth failure.
- Use respx or a local stub rather than the real test-runner in unit tests.

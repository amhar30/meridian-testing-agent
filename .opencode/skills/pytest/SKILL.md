---
name: pytest
description: Use when generating, reviewing, or running Meridian pytest suites, including reports/generated tests and tests/ project tests.
---

# pytest in Meridian

Read AGENTS.md §3.3 and docs/architecture.md §3 before generating tests.

## Generated Tests
- Generated file: `reports/generated/<module_name>_tests.py`; never edit the target module.
- Cover normal paths, boundaries, invalid inputs, exceptions, forgotten states, and important dependency interactions.
- Assertions must verify specific expected behavior and values; mutation catch rate is the primary metric.
- Reject empty tests, `assert True`, and assertions that cannot distinguish correct from incorrect behavior.
- Keep each module's suite deterministic, offline, and within the test-runner timeout (default 7 minutes).
- No network, production credentials, LLM keys, or Docker socket access in tests.
- Use `pytest.raises` with specific exception types and `match` where stable.
- Tests execute only inside the isolated test-runner container, never in the app process.

## Project Tests
- Put unit tests in `tests/unit/`, integration in `tests/integration/`, security in `tests/security/`, evaluation in `tests/evaluation/`.
- Use fixtures from `tests/fixtures/`; avoid sleeps and external services.
- Run focused tests first, then the relevant suite before reporting completion.

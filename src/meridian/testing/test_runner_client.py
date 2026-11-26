"""Test Runner Client - deterministic, no LLM.

Sends generated pytest test code to the isolated test-runner service via HTTP.
Applies hard timeouts and stores structured results in LangGraph state.

See AGENTS.md §3.4 for full requirements.
"""

from __future__ import annotations

import json
from typing import Any

from httpx import Client, ConnectError, HTTPError, TimeoutException

from meridian.orchestrator.state import (
    TEST_EXECUTION_TIMEOUT_SECONDS,
    MeridianState,
)


def execute_tests(
    tests: list[str],
    module_name: str,
    timeout: float = TEST_EXECUTION_TIMEOUT_SECONDS,
    base_url: str = "http://127.0.0.1:8000",
) -> dict[str, Any]:
    """Send generated tests to the test-runner service and collect results.

    Args:
        tests: List of test file contents (pytest test functions).
        module_name: Name of the module being tested (for error reporting).
        timeout: Maximum seconds to wait for the full execution. Defaults to
            TEST_EXECUTION_TIMEOUT_SECONDS (7 minutes, per architecture constraint).
        base_url: Base URL of the test-runner HTTP service.

    Returns:
        Dict with keys:
        - "test_results": list[dict] — per-test results with name, passed, traceback
        - "module_name": the module name
        - "error": error string if the service is unreachable (no exception thrown)

    Does NOT execute pytest in the main application process. Communicates
    with the test-runner service via HTTP. If the service is unavailable,
    returns a structured error result rather than raising.
    """
    if not tests:
        return {
            "test_results": [],
            "module_name": module_name,
            "error": "no tests provided",
        }

    test_results: list[dict[str, Any]] = []

    with Client(base_url=base_url, timeout=timeout) as client:
        for test_code in tests:
            try:
                resp = client.post("/run-tests", json={"tests": [test_code], "module": module_name})
                resp.raise_for_status()
                data = resp.json()
                # test-runner returns a list of per-test results; take the first
                # since we send one test. If it's a single dict, wrap it.
                if isinstance(data, list):
                    result = data[0] if data else {}
                else:
                    result = data
                if result:  # skip empty dict/list
                    test_results.append(result)
            except TimeoutException:
                test_results.append({
                    "name": f"{module_name}_test_{len(test_results)}",
                    "passed": None,
                    "traceback": f"Execution timed out after {timeout}s",
                    "note": "timeout",
                })
            except ConnectError:
                # Service unreachable — return structured error, don't raise
                return {
                    "test_results": test_results,
                    "module_name": module_name,
                    "error": f"test-runner service unreachable at {base_url}",
                }
            except HTTPError as e:
                test_results.append({
                    "name": f"{module_name}_test_{len(test_results)}",
                    "passed": None,
                    "traceback": "HTTP error",
                    "note": "http_error",
                })
            except Exception as e:
                test_results.append({
                    "name": f"{module_name}_test_{len(test_results)}",
                    "passed": None,
                    "traceback": f"unexpected error: {e}",
                    "note": "unexpected_error",
                })

    return {"test_results": test_results, "module_name": module_name, "error": None}
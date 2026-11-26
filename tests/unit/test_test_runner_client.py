"""Unit tests for Meridian test_runner_client.

Uses unittest.mock.patch with autospec for proper HTTP mocking.
No Docker required.
"""

import sys
sys.path.insert(0, sys.path[0] + "/.." if "/src" in sys.path[0] else "src")

from unittest.mock import patch, Mock

from httpx import Client

from meridian.testing.test_runner_client import execute_tests


def test_execute_tests_no_tests():
    """Empty test list returns early."""
    result = execute_tests([], "test_mod")
    assert result["test_results"] == []
    assert result["module_name"] == "test_mod"
    assert result["error"] == "no tests provided"


def test_execute_tests_success():
    """Successful HTTP response returns test results."""
    with patch.object(Client, "post", autospec=True) as mock_post:
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"name": "test_passed", "passed": True, "traceback": None}

        result = execute_tests(["def test_x(): assert True"], "my_module")

    assert result["test_results"] == [{"name": "test_passed", "passed": True, "traceback": None}]
    assert result["module_name"] == "my_module"
    assert result["error"] is None


def test_execute_tests_timeout():
    """Timeout during HTTP call is caught and reported."""
    from httpx import Client, TimeoutException

    with patch.object(Client, "post", autospec=True) as mock_post:
        mock_post.side_effect = TimeoutException("Request timed out")

        result = execute_tests(["def test_x(): pass"], "my_module", timeout=5)

    assert result["error"] is None  # timeout is per-test, not module-level
    assert len(result["test_results"]) == 1
    assert "timed out" in result["test_results"][0]["traceback"]


def test_execute_tests_connect_error():
    """Connection error returns structured error, doesn't raise."""
    from httpx import Client, ConnectError

    with patch.object(Client, "post", autospec=True) as mock_post:
        mock_post.side_effect = ConnectError("Connection refused")

        result = execute_tests(["def test_x(): pass"], "my_module")

    assert result["error"] == "test-runner service unreachable at http://127.0.0.1:8000"
    assert result["test_results"] == []  # no results returned on connect error
    assert result["module_name"] == "my_module"


def test_execute_tests_http_error():
    """HTTP error (non-200) is caught and reported."""
    from httpx import HTTPStatusError

    with patch.object(Client, "post", autospec=True) as mock_post:
        mock_post.side_effect = HTTPStatusError(
            "500 Server Error", request=None, response=Mock()
        )

        result = execute_tests(["def test_x(): pass"], "my_module")

    assert result["error"] is None  # HTTP error doesn't set the 'error' key
    assert len(result["test_results"]) == 1
    assert result["test_results"][0]["note"] == "http_error"


def test_execute_tests_unexpected_error():
    """Unexpected error is caught and reported."""
    from httpx import Client

    with patch.object(Client, "post", autospec=True) as mock_post:
        mock_post.side_effect = ValueError("something went wrong")

        result = execute_tests(["def test_x(): pass"], "my_module")

    assert result["error"] is None
    assert len(result["test_results"]) == 1
    assert "unexpected error" in result["test_results"][0]["traceback"]


def test_execute_tests_empty_json():
    """HTTP response with empty JSON result (no test results)."""
    with patch.object(Client, "post", autospec=True) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}

        result = execute_tests(["def test_x(): pass"], "my_module")

    assert result["test_results"] == []
    assert result["module_name"] == "my_module"
    assert result["error"] is None


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
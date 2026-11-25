---
name: fastmcp
description: Use when implementing or changing Meridian's read-only MCP tools (read_file, list_symbols, read_docstrings) in src/meridian/mcp.
---

# FastMCP in Meridian

Read AGENTS.md §12 and docs/architecture.md §11 before editing tools.

## Server
- Implement the MCP server in `src/meridian/mcp/server.py`; register tools in `tool_registry.py`.
- Expose only `read_file(path)`, `list_symbols(path)`, and `read_docstrings(path)` initially.
- Tools are read-only and operate on the target repository mounted read-only in the `mcp-server` container.
- Give each agent only the tools it needs; Comprehension uses these three.
- Log tool calls without logging source secrets or credentials.

## Security
- Resolve and validate every path against the allowed repository root.
- Reject path traversal, symlinks escaping the root, absolute host paths, and non-regular files.
- No unrestricted filesystem access, production database access, or source modification.
- Enforce request size and file-size limits; fail closed on errors.
- Return structured errors rather than tracebacks.

## Integration
- The app uses MCP tools for comprehension/analysis, not direct host filesystem reads.
- Keep tool schemas stable; update tests in `tests/security/` and `tests/integration/` when behavior changes.
- Do not expose test execution or write operations through MCP.

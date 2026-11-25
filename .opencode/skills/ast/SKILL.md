---
name: ast
description: Use when implementing Meridian Python AST analysis in src/meridian/analysis or symbol/docstring extraction for comprehension.
---

# Python AST in Meridian

Read AGENTS.md §3.2 and docs/architecture.md §4 before editing analysis.

## Use
- `src/meridian/analysis/ast_analyzer.py` extracts functions, classes, imports, docstrings, and risky paths.
- `dependency_analyzer.py` maps imports and internal dependencies for comprehension.
- Use stdlib `ast`; do not import or execute the target module in the app process.
- Parse only files inside the allowed repository root; reject traversal and non-Python files.
- Handle `SyntaxError` and encoding errors as structured analysis failures.

## Output
- Provide deterministic symbol facts to the Comprehension Agent and `list_symbols`/`read_docstrings` MCP tools.
- Identify public API, normal behavior, boundary conditions, exceptions, and risky execution paths.
- Keep summaries structured and token-bounded; avoid dumping entire source into prompts.
- Never modify target source files.

## Verify
- Add unit fixtures under `tests/fixtures/` covering classes, decorators, async functions, nested scopes, and syntax errors.
- Test path validation under `tests/security/`.

---
name: python
description: Use when writing or reviewing Meridian Python code in src/meridian, tests, scripts, or evaluation; applies project package layout and constraints.
---

# Python in Meridian

Target Python 3.11.9, matching docs/architecture.md reproducibility records.
Read AGENTS.md and docs/architecture.md before changing architecture.

## Layout
- Package root: `src/meridian/`; import as `from meridian...` (src layout).
- Orchestrator: `orchestrator/`; agents: `agents/`; deterministic helpers: `testing/`, `analysis/`, `memory/`.
- Tests live in `tests/{unit,integration,evaluation,security}`.
- Never modify target production modules; Meridian only reads them.

## Rules
- Add type hints and docstrings to public functions; keep `MeridianState` typed in `orchestrator/state.py`.
- Deterministic nodes must not call an LLM.
- Use `pathlib.Path` and config values; do not hardcode host paths or secrets.
- Keep module context within token budgets; avoid unnecessary LLM calls.
- The stack is fixed (AGENTS.md §2); ask before adding dependencies.
- Temperature is 0.2 for generation and diagnosis.
- Verify with project tests or a focused pytest run before reporting done.

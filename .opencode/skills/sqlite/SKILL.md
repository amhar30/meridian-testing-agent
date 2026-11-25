---
name: sqlite
description: Use when implementing Meridian long-term memory or audit storage in src/meridian/memory/sqlite_store.py, not LangGraph checkpointing.
---

# SQLite in Meridian

Read AGENTS.md §11 and docs/architecture.md §10 before editing storage.

## Responsibilities
- `sqlite_store.py`: long-term memory — module summaries, confirmed conventions, approved test outcomes, execution metadata.
- `checkpointing.py`: LangGraph checkpoints for interrupt/resume; keep schema and access separate.
- `working_memory.py`: current run context; not a substitute for persistent memory.
- SQLite is the only long-term store; no Supabase or PostgreSQL.

## Rules
- Use parameterized SQL, explicit transactions, and a configurable database path.
- Store only useful, non-sensitive history; no secrets, credentials, LLM keys, or unnecessary source.
- Keep memory access controlled and auditable; log writes without exposing source contents.
- Record approval audit data (approver, decision, timestamp, rejection reason) durably.
- Make schema changes explicit and reproducible; avoid destructive migrations without approval.
- Do not mix checkpoint tables with long-term memory tables even if using one database file.

## Verify
- Add unit tests in `tests/unit/` for schema, retrieval, and sensitive-data rejection.
- Confirm checkpoint resume still works after memory schema changes.

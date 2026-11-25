---
name: langgraph-checkpointing
description: Use when implementing Meridian human-approval persistence or resuming interrupted LangGraph runs with SqliteSaver in memory/checkpointing.py.
---

# Checkpointing in Meridian

Read AGENTS.md §7 and docs/architecture.md §10 before editing.

## Requirements
- Use a persistent SQLite LangGraph checkpointer: `SqliteSaver` or `AsyncSqliteSaver`.
- Keep checkpointing in `src/meridian/memory/checkpointing.py`; it is distinct from long-term memory in `sqlite_store.py`.
- The Human Approval Gate uses `interrupt()`; the graph must pause before test merge.
- Resume with the same `thread_id` and a `Command(resume=...)` decision.
- Approval state must survive application restarts and container restarts.
- Choose sync or async checkpointing to match how the graph is executed; do not mix.

## Data Rules
- Persist only graph execution data needed to resume; do not store secrets or LLM credentials.
- Record engineer decision, feedback/rejection reason, approver identity, and timestamp for audit.
- Rejected tests must not proceed to merge.
- Checkpointer tables stay separate from long-term memory tables even if sharing one SQLite file.
- Provide cleanup/retention handling for old threads.

## Verify
- Test pause → restart → resume with the same thread ID.
- Test reject and approve paths, and verify no autonomous merge occurs.

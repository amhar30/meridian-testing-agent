---
name: langfuse
description: Use when adding or changing Meridian Langfuse tracing, spans, token/cost tracking, or observability configuration.
---

# Langfuse in Meridian

Read AGENTS.md §10 and docs/architecture.md §9 before editing observability.

## Tracing
- One trace per module run: `module_run_{module_name}_{timestamp}`; store its ID in `MeridianState.langfuse_trace_id`.
- One span per stage: `comprehension`, `generation`, `test_execution`, `diagnosis`, `quality_check`, `mutation_testing`, `report`, `human_approval`.
- Implement in `src/meridian/observability/langfuse_client.py` and `tracing.py`.
- Record input/output tokens, cost_usd, latency_ms, retry counts, errors, and approval outcomes where available.
- Deterministic nodes record latency and metadata only; never invent token usage or cost.
- Record discontinued/failed runs and flush traces on errors and shutdown.

## Rules
- Use the local `langfuse` Compose service or configured endpoint; credentials come from env.
- Never put API keys or credentials in traces, state, logs, or generated reports.
- Keep trace/span names stable so dashboards and evaluation comparisons remain valid.
- Cost reporting must separate actual API spend from estimated engineer-time savings.
- Langfuse failures must not silently break a module run; log the observability error and continue.

## Verify
- Run one module end-to-end and confirm the trace contains all expected spans and accurate retry counts.

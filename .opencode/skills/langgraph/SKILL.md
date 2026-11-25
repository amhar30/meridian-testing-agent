---
name: langgraph
description: Use when editing Meridian's LangGraph orchestrator StateGraph, nodes, routing, or feedback loops in src/meridian/orchestrator.
---

# LangGraph in Meridian

Read AGENTS.md and docs/architecture.md §3-6 before wiring nodes.

## Graph Contract
- Eight nodes: Orchestrator, Comprehension, Generator, Test Runner Client, Diagnosis, Assertion Quality Check, Reporter, Human Approval.
- Flow: Comprehension → Generation → Test Execution → Diagnosis → Quality Check → Reporter → Approval.
- `graph.py` compiles; `nodes.py` implements entry points; `routing.py` owns conditionals; `approval.py` owns interrupt().

## State
- `MeridianState` in `state.py` is the single shared state; extend consistently across all nodes.
- Track `retry_count`/`retry_cap` (Loop 1, default 5) and `quality_retry_count`/`quality_retry_cap` (Loop 2, default 3) separately.
- Never store secrets, credentials, or unnecessary personal data in state.

## Rules
- Loop 1: Diagnosis → Generator → Test Runner → Diagnosis for invalid tests.
- Loop 2: Quality Check → Comprehension → Generator → Test Runner for weak assertions.
- Refinement is routing behavior; do not add a separate refinement agent.
- Test Runner Client and Assertion Quality Check are deterministic, not LLM agents.
- Enforce the 10-minute module deadline and both loop caps; mark capped modules partially covered.
- Do not redesign the approved graph without project-owner approval.

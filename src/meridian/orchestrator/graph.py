"""Compiles the Meridian eight-node LangGraph StateGraph.

Wires the orchestrator nodes, both bounded feedback loops, and the human
approval gate into a single compiled graph with a persistent checkpointer.

Node order (linear flow):
  orchestrator -> comprehension -> generator -> test_runner_client ->
  diagnosis -> assertion_quality_check -> reporter -> human_approval

Conditional routing:
  Loop 1: diagnosis --(bad test, under cap)--> generator (retry_count++)
          diagnosis --(cap reached / real bug)--> assertion_quality_check
  Loop 2: quality_check --(weak assertion, under cap)--> comprehension
                              (quality_retry_count++)
          quality_check --(all good / cap reached)--> reporter

See docs/architecture.md sections 3-5 and AGENTS.md sections 3-4.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from meridian.orchestrator.state import MeridianState
from meridian.orchestrator import nodes, routing, approval


def build_graph(checkpointer=None):
    """Build and compile the eight-node Meridian StateGraph.

    Args:
        checkpointer: optional LangGraph checkpointer. Defaults to MemorySaver
                      (in-memory). For production, pass a SQLite-backed
                      checkpointer from src/meridian/memory/checkpointing.py
                      so interrupt/resume survives restarts.

    Returns a compiled LangGraph graph (CompiledStateGraph).
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(MeridianState)

    # --- Register the eight nodes -----------------------------------------
    builder.add_node(routing.N_ORCHESTRATOR, nodes.orchestrator_node)
    builder.add_node(routing.N_COMPREHENSION, nodes.comprehension_node)
    builder.add_node(routing.N_GENERATOR, nodes.generator_node)
    builder.add_node(
        routing.N_TEST_RUNNER_CLIENT, nodes.test_runner_client_node
    )
    builder.add_node(routing.N_DIAGNOSIS, nodes.diagnosis_node)
    builder.add_node(
        routing.N_QUALITY_CHECK, nodes.assertion_quality_check_node
    )
    builder.add_node(routing.N_REPORTER, nodes.reporter_node)
    builder.add_node(routing.N_HUMAN_APPROVAL, approval.human_approval_node)

    # --- Entry point -------------------------------------------------------
    builder.add_edge(START, routing.N_ORCHESTRATOR)

    # --- Linear flow: orchestrator -> ... -> reporter ---------------------
    builder.add_edge(routing.N_ORCHESTRATOR, routing.N_COMPREHENSION)
    builder.add_edge(routing.N_COMPREHENSION, routing.N_GENERATOR)
    builder.add_edge(routing.N_GENERATOR, routing.N_TEST_RUNNER_CLIENT)
    builder.add_edge(routing.N_TEST_RUNNER_CLIENT, routing.N_DIAGNOSIS)

    # --- Loop 1: diagnosis -> generator (retry) or quality check ----------
    # The routing function returns a Command (with counter increment) or a
    # plain node name; no path_map is used so Command objects pass through.
    builder.add_conditional_edges(
        routing.N_DIAGNOSIS,
        routing.route_after_diagnosis,
    )

    # --- Loop 2: quality check -> comprehension (retry) or reporter -------
    builder.add_conditional_edges(
        routing.N_QUALITY_CHECK,
        routing.route_after_quality_check,
    )

    # --- Reporter -> human approval -> END --------------------------------
    builder.add_edge(routing.N_REPORTER, routing.N_HUMAN_APPROVAL)
    builder.add_edge(routing.N_HUMAN_APPROVAL, END)

    graph = builder.compile(checkpointer=checkpointer)
    return graph


# Default compiled graph using the in-memory checkpointer.
# Replace the checkpointer with SQLite-backed checkpointing (see
# docs/architecture.md section 10) before deploying to production.
graph = build_graph()

__all__ = ["build_graph", "graph"]

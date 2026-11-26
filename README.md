# Meridian — Agentic AI Testing & Quality Assurance System

**An AI-powered system that understands Python code, generates meaningful tests, executes them in an isolated environment, and improves test quality through iterative feedback.**

## Overview

Meridian is an Agentic AI Testing and Quality Assurance system designed to help developers improve test coverage and identify potential software defects in unfamiliar Python codebases.

Instead of simply generating test cases, Meridian follows an iterative workflow:

1. Understand the target Python module.
2. Generate tests based on the module's behavior.
3. Execute the generated tests in an isolated environment.
4. Analyze test failures and identify whether the issue is with the test or the source code.
5. Refine tests when necessary.
6. Evaluate whether the generated tests contain meaningful assertions.
7. Produce a report for developer review.
8. Require human approval before tests are accepted.

The goal is to generate useful, reliable, and reviewable tests—not just increase coverage numbers.

## The Problem

Software projects often contain legacy modules with limited or outdated test coverage.

Developers working with unfamiliar code can spend considerable time understanding existing behavior and writing tests. Weak tests may also pass without checking anything meaningful.

Meridian aims to address these challenges through an agentic workflow that combines code comprehension, test generation, execution, diagnosis, and quality evaluation.

## Key Objectives

- Understand unfamiliar Python modules.
- Generate tests for normal behavior, edge cases, and error conditions.
- Execute tests safely in isolated environments.
- Diagnose test failures and refine incorrect tests.
- Detect weak or meaningless assertions.
- Evaluate test effectiveness through mutation testing.
- Provide reviewable test files and coverage reports.
- Keep developers in control through human approval.

## Architecture

Meridian uses **LangGraph** to coordinate its eight workflow nodes.

### Agentic Workflow

| Node | Responsibility |
|---|---|
| Orchestrator | Coordinates the overall workflow |
| Comprehension Agent | Analyzes source code and understands module behavior |
| Generator Agent | Generates Python test cases |
| Test Runner Client | Sends test execution requests to the isolated test runner |
| Diagnosis Agent | Analyzes failures and determines the next action |
| Assertion Quality Check | Evaluates whether tests contain meaningful assertions |
| Reporter | Produces the final test report |
| Human Approval Gate | Allows a developer to approve, reject, or request changes |

### Iterative Testing

Meridian uses two bounded feedback loops:

**Loop 1 — Test Refinement**

When generated tests fail, the Diagnosis Agent analyzes the failure and can send the workflow back through test generation and execution.

**Loop 2 — Assertion Quality Improvement**

When tests do not meet assertion-quality requirements, the workflow can revisit code comprehension, regenerate tests, and execute them again.

Both loops have retry limits to prevent endless execution.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main application language |
| LangGraph | Agentic workflow orchestration |
| LLMs | Code comprehension, test generation, and diagnosis |
| MCP | Controlled access to source-code information |
| Pytest | Python test execution |
| Docker | Isolated test execution |
| SQLite | Persistent state and workflow checkpointing |
| Langfuse | LLM observability and tracing |
| Docker Compose | Multi-service development environment |

*Some integrations and components are still under development.*

## Security and Isolation

Meridian is designed to execute generated tests without exposing the host environment.

Planned sandbox controls include:

- Isolated Docker containers for test execution.
- No host Docker socket exposure.
- No privileged child test containers.
- Restricted network access for test execution.
- CPU, memory, process, and execution-time limits.
- Read-only access to original source code.
- Controlled storage for generated tests and results.
- Cleanup of temporary execution containers.

The main application communicates with the test runner through HTTP rather than executing tests directly on the host.

## Evaluation Strategy

Meridian's effectiveness should be measured through actual testing results, not just code coverage.

The evaluation plan includes:

- Testing against real open-source Python modules.
- Evaluating normal, edge-case, and error-handling behavior.
- Using mutation testing to measure whether generated tests detect introduced defects.
- Measuring meaningful assertion quality.
- Tracking execution time and retry counts.
- Measuring cost per module.
- Checking consistency across repeated runs.

**Mutation Score:**

`Mutation Score = (Killed Mutants / (Killed Mutants + Surviving Mutants)) × 100`

Mutants that fail to execute or are excluded should be reported separately.

## Human-in-the-Loop Approval

Meridian does not automatically merge generated tests.

Developers can review the generated test files and reports before accepting them. The approval workflow supports:

- Approve
- Reject
- Edit and approve

This keeps the developer responsible for the final decision.

## Project Status

Meridian is currently under development.

| Component | Status |
|---|---|
| LangGraph workflow foundation | Implemented |
| Workflow state management | Implemented |
| Bounded retry routing | Implemented |
| Human approval interruption | Implemented |
| Test Runner HTTP client | Implemented |
| Unit tests for workflow foundations | Implemented |
| LLM provider integration | In progress |
| Code comprehension implementation | In progress |
| Test generation implementation | In progress |
| Failure diagnosis and refinement | In progress |
| Assertion quality evaluation | In progress |
| Docker sandbox integration | In progress |
| MCP server integration | In progress |
| Langfuse observability | Planned |
| Mutation testing evaluation | Planned |
| User interface and deployment | Planned |

*Status reflects the current development plan and should be updated as components are completed and verified.*

## Getting Started

### Prerequisites

- Python 3.10 or later
- Docker Desktop with WSL2 integration (for Windows development)
- Git
- An LLM provider API key (once provider integration is configured)

### Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Merydian
```

### Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
pytest
```

> Setup and execution commands may change as the application and Docker services are integrated. Check the project configuration and documentation for the latest instructions.

## Project Structure

```text
Merydian/
├── .opencode/
│   ├── agents/
│   └── skills/
├── docs/
│   ├── adr/
│   ├── architecture.md
│   ├── client-brief.md
│   ├── engagement-handbook.md
│   └── requirements-traceability.md
├── src/
│   └── meridian/
│       ├── memory/
│       ├── orchestrator/
│       └── testing/
├── tests/
│   └── unit/
├── AGENTS.md
├── progress.md
└── README.md
```

## Project Goals

Meridian aims to demonstrate how agentic AI can improve software testing by combining autonomous reasoning with deterministic execution, measurable evaluation, and human oversight.

**Our focus: Meaningful tests. Reliable execution. Measurable quality.**

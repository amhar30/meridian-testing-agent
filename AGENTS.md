# Meridian Testing Agent — AGENTS.md
This file is the single source of truth for OpenCode and all subagents working on this project.
**Read this file and the relevant project documentation before writing or modifying any code.**
All subagents must follow these requirements. No subagent may independently redesign the architecture, change the technology stack, or introduce new major components without explicit approval from the project owner.

---

## Documentation Reading Rules

- Read AGENTS.md first.
- Read docs/architecture.md before architectural implementation.
- Treat docs/original/architecture.pdf as the original reference.
- Do not change the approved architecture without project-owner approval.
- Read docs/client-brief.md when checking client requirements.
- Read docs/engagement-handbook.md for marking criteria and deliverables.
- Read docs/project-brief.md for engineering standards and delivery rules.
- Read docs/client-brief.md when checking client requirements.
- Read docs/architecture.md before architectural implementation.
- Read progress.md to understand what has been completed and what comes next.
- Read docs/repository-inspection.md when inspecting the target repository (add later).
- Read docs/proposed-modules.md when target modules are confirmed (add later).
- Do not repeatedly load entire documents when only a specific section is needed.
- Retrieve only relevant sections whenever possible.
- Original PDFs in docs/original/ are reference copies.
- Markdown documents are the primary working references.

---
# 1. What This System Does
Meridian Testing Agent is an AI-powered regression-testing system for unfamiliar Python codebases.
It:
1.	Reads and analyzes an unfamiliar Python module.
2.	Understands its intended behavior, public API, edge cases, and risky execution paths.
3.	Generates meaningful pytest tests.
4.	Executes generated tests in an isolated Docker-based environment.
5.	Diagnoses test failures, distinguishing invalid tests from likely defects in the original module.
6.	Refines generated tests using bounded feedback loops.
7.	Evaluates test effectiveness through mutation testing.
8.	Produces a reviewable test file and an execution report.
9.	Pauses for explicit engineer approval before any test is merged.
**The primary quality metric is mutation catch rate, not code coverage percentage.**
The system must generate tests that meaningfully exercise real behavior, not tests that simply pass.
---
# 2. Non-Negotiable Technology Stack
Do not replace these technologies without explicit project-owner approval.
| Area | Technology |
|---|---|
| Orchestration | LangGraph StateGraph |
| Shared state | Python TypedDict |
| Human approval | LangGraph interrupt() |
| LLM | Configurable provider through environment variables |
| Default model | Configurable; use a currently supported model identifier |
| LLM temperature | 0.2 for generation and diagnosis |
| API | FastAPI |
| Observability | Langfuse |
| Test framework | pytest |
| Test execution | Isolated Docker execution environment |
| Code analysis | Python AST |
| Tool integration | MCP |
| Working memory | LangGraph state |
| Long-term memory | SQLite |
| Container orchestration | Docker Compose |
| CI/CD | GitHub Actions |
| Mutation testing | mutmut |
| Version control | Git and GitHub |
Do not assume a model identifier is valid without checking the selected provider's current supported models.
---
# 3. Project Architecture and File Responsibilities
Maintain clear separation of responsibilities.
## 3.1 Orchestrator
Location:
src/meridian/orchestrator/
Files:
•	graph.py — Defines and compiles the LangGraph StateGraph.
•	state.py — Defines the shared MeridianState TypedDict.
•	nodes.py — Implements node entry points and graph workflow coordination.
•	routing.py — Implements conditional routing and both feedback loops.
•	approval.py — Implements human approval using LangGraph interrupt().
The orchestrator must:
•	Start a module execution.
•	Initialize the shared state.
•	Set execution budgets and retry limits.
•	Route execution through the required agent nodes.
•	Track execution status.
•	Handle feedback loops.
•	Pause for human approval.
•	Resume or reject execution based on the engineer's decision.
•	Continue to the next module when the current module is completed or rejected.
Refinement is graph routing behavior. Do not create a separate test-refinement agent.
## 3.2 Comprehension Agent
Location:
src/meridian/agents/code_understanding.py
Responsibilities:
•	Read unfamiliar Python modules using approved MCP tools.
•	Understand functions, classes, imports, dependencies, and public interfaces.
•	Identify normal behavior, boundaries, exceptions, and risky paths.
•	Produce a structured comprehension summary.
•	Provide expected behavior and relevant context to the Generator Agent.
The agent must not modify production source code.
## 3.3 Generator Agent
Location:
src/meridian/agents/test_generation.py
Responsibilities:
•	Generate pytest test cases from the comprehension summary.
•	Generate tests for:
o	Normal execution paths.
o	Boundary conditions.
o	Invalid inputs.
o	Exceptions and error handling.
o	Forgotten states.
o	Important dependencies and interactions.
•	Accept feedback from the Diagnosis Agent.
•	Accept quality-check feedback through the Comprehension Agent.
•	Regenerate tests based on specific feedback.
Requirements:
•	Use temperature 0.2.
•	Produce meaningful, deterministic, reviewable test cases.
•	Avoid trivial assertions.
•	Do not modify the original production module.
## 3.4 Test Runner Client
Location:
src/meridian/testing/test_runner_client.py
**This is agent-side application code. It is NOT the Docker test-runner server.**
Responsibilities:
•	Send generated test code and the required execution context to the test-runner service through HTTP.
•	Receive structured JSON execution results.
•	Apply a hard timeout of 10 minutes per module.
•	Handle service errors and timeouts.
•	Store per-test results, failures, and tracebacks in LangGraph state.
It must not execute untrusted pytest code in the main application process.
## 3.5 Test Runner Server
Location:
src/meridian/test_runner/server.py
**This code runs inside the Docker test-runner service container. It is separate from test_runner_client.py.**
Responsibilities:
•	Expose the test execution HTTP endpoint, including POST /run-tests.
•	Validate incoming requests.
•	Coordinate isolated test execution.
•	Return structured JSON results.
•	Handle execution errors and timeouts.
The HTTP server must not directly execute untrusted test code inside its own process.
## 3.6 Test Execution Runner
Location:
src/meridian/test_runner/runner.py
Responsibilities:
•	Coordinate actual pytest execution.
•	Prepare the temporary execution workspace.
•	Execute pytest in a separately restricted execution environment.
•	Collect test results, tracebacks, and execution metadata.
•	Return structured results to the server.
The test-runner service and the untrusted test execution environment are separate security boundaries.
## 3.7 Assertion Quality Checker
Location:
src/meridian/testing/assertion_checker.py
This is deterministic code, NOT an LLM agent.
Responsibilities:
•	Inspect generated test cases.
•	Detect empty test bodies.
•	Reject meaningless assertions such as assert True.
•	Detect trivially weak assertions.
•	Identify tests that pass without meaningfully checking behavior.
•	Return actionable quality feedback.
Weak tests must be routed back to the Comprehension Agent.
## 3.8 Failure Diagnosis Agent
Location:
src/meridian/agents/failure_diagnosis.py
Responsibilities:
•	Analyze failed test results.
•	Examine relevant original module code and test tracebacks.
•	Distinguish:
o	Incorrect generated tests.
o	Incorrect assumptions about behavior.
o	Import and dependency problems.
o	Test environment failures.
o	Likely genuine bugs in the original module.
•	Send invalid tests back to the Generator Agent.
•	Record likely production-code defects in bug_findings.
Do not classify every failed test as a production bug.
## 3.9 Reporter
Location:
src/meridian/agents/report_generation.py
Responsibilities:
Generate:
•	Final pytest test file.
•	Module execution report.
•	Mutation testing results, when available.
•	Bug findings.
•	Retry count.
•	Token usage and cost.
•	Execution duration.
•	Quality-check results.
Output locations:
reports/generated/<module_name>_tests.py
reports/generated/<module_name>_report.md
Reports must clearly distinguish confirmed execution results from AI-generated suspected defects.
---
# 4. Eight-Node LangGraph Workflow
The system has eight logical workflow nodes.
1.	Orchestrator.
2.	Comprehension Agent.
3.	Generator Agent.
4.	Test Runner Client.
5.	Diagnosis Agent.
6.	Assertion Quality Check.
7.	Reporter.
8.	Human Approval Gate.
The Test Runner Client and Assertion Quality Check are deterministic components, not LLM agents.
Required execution flow:
Comprehension → Generation → Test Execution → Diagnosis → Assertion Quality Check → Reporter → Human Approval.
Conditional routing determines whether execution continues, loops back, or terminates.
---
# 5. Two Critical Feedback Loops
Both loops must be implemented through orchestrator/routing.py and connected in orchestrator/graph.py.
## Loop 1: Diagnosis Agent → Generator Agent
Condition:
The Diagnosis Agent determines that a failed test is invalid or based on an incorrect assumption rather than a likely production-code defect.
Flow:
Diagnosis Agent → Generator Agent → Test Runner Client → Diagnosis Agent.
Requirements:
•	Increment retry_count.
•	Maximum five refinement cycles per module.
•	Stop retrying when retry_cap is reached.
•	Mark the module as partially covered when the retry limit is reached.
•	Continue to the quality-check and reporting stages as appropriate.
## Loop 2: Assertion Quality Check → Comprehension Agent
Condition:
A generated test passes but does not meaningfully verify expected behavior.
Flow:
Assertion Quality Check → Comprehension Agent → Generator Agent → Test Runner Client.
Requirements:
•	Send specific quality feedback.
•	Ask the Comprehension Agent to reconsider expected behavior and identify concrete expected values.
•	Regenerate meaningful assertions.
•	Re-execute the generated tests.
**Safety requirement:** This loop must not run indefinitely. Implement a configurable quality-loop safety limit and an overall execution budget. The default quality-loop limit must be documented and configurable.
The five-cycle diagnosis retry limit and the quality-loop limit must be tracked separately.
---
# 6. Shared LangGraph State
Location:
src/meridian/orchestrator/state.py
Use a typed shared state similar to:
from typing import TypedDict


class MeridianState(TypedDict):
    module_name: str
    module_path: str

    comprehension_summary: str
    generated_tests: list[str]

    test_results: list[dict]
    bug_findings: list[str]

    retry_count: int
    retry_cap: int

    quality_retry_count: int
    quality_retry_cap: int

    token_cost_usd: float

    approval_decision: str | None
    approval_feedback: str | None

    langfuse_trace_id: str

    quality_check_feedback: str | None

    execution_duration_seconds: float

    status: str
State may be extended when implementation requires additional fields, but changes must remain consistent across all nodes.
Do not store secrets, credentials, or unnecessary personal information in LangGraph state.
---
# 7. Human-in-the-Loop Approval
Location:
src/meridian/orchestrator/approval.py
Use LangGraph interrupt() to pause execution.
The engineer must be able to review:
•	Generated test file.
•	Execution report.
•	Bug findings.
•	Mutation results, when available.
•	Retry count.
•	Token cost.
•	Execution duration.
Possible decisions:
•	Approve.
•	Edit and approve.
•	Reject.
Requirements:
1.	The graph must pause before the test-merge stage.
2.	Use a persistent LangGraph checkpointer.
3.	Resume using the same thread ID.
4.	Record the engineer's decision.
5.	Record rejection reasons where provided.
6.	Rejected tests must not proceed to merge.
7.	Approved tests may proceed to a separately authorized GitHub PR or merge workflow.
8.	Never perform an autonomous merge without explicit engineer authorization.
Approval and merge are separate actions. The audit trail must identify who approved the tests and when.
---
# 8. Docker Architecture and Security
The root docker-compose.yml must coordinate the application services.
Four primary services:
## 8.1 app
•	FastAPI.
•	LangGraph orchestrator.
•	Agent implementations.
•	MCP clients.
•	Langfuse integration.
•	SQLite memory access where required.
## 8.2 test-runner
•	Minimal Python image.
•	Contains server.py and runner.py.
•	Exposes POST /run-tests.
•	Coordinates isolated pytest execution.
•	Returns structured JSON results.
## 8.3 langfuse
•	Official Langfuse deployment image or supported deployment configuration.
•	Provides local observability where configured.
•	Must use a supported and properly configured deployment setup.
## 8.4 mcp-server
•	Provides controlled read-only repository access.
•	Exposes approved repository inspection tools.
•	Must not provide unrestricted filesystem access.
## 8.5 Test Execution Isolation
Untrusted generated test code must execute in a separately restricted environment.
Minimum security requirements:
•	No internet access from the test execution environment.
•	No production credentials.
•	No LLM API credentials.
•	No Docker socket exposed to untrusted test code.
•	No privileged containers.
•	Read-only access to the original source.
•	Temporary writable workspace for execution.
•	Controlled access to copied source files and required dependencies.
•	CPU, memory, process, and execution-time limits.
•	Request validation and authentication between the app and test-runner service.
•	Restricted filesystem access.
•	Cleanup of temporary execution files.
•	Structured output validation.
Do not assume that placing pytest inside a Docker container automatically makes execution secure.
The test-runner HTTP service should coordinate the sandbox; it must not execute arbitrary submitted code inside its own server process.
---
# 9. Mutation Testing — Primary Evaluation Metric
Tool: mutmut
Main script:
scripts/run_evaluation.py
Evaluation directory:
evaluation/
Workflow:
1.	Prepare an isolated copy of the target module.
2.	Apply mutations to the isolated copy.
3.	Run the generated tests against the mutated version.
4.	Record killed and surviving mutants.
5.	Identify which tests failed to detect surviving mutations.
6.	Calculate mutation catch rate.
Formula:
Mutation Catch Rate =
(Mutations Killed / Total Mutations) × 100
Output:
evaluation/evaluation_results/<module_name>_eval.json
Important:
•	Never mutate the original production module.
•	Run mutation testing in an isolated temporary workspace.
•	Preserve the original module unchanged.
•	Record equivalent mutants or excluded mutants transparently.
•	Do not report a misleading score when mutations could not be executed.
•	Coverage percentage may be reported as supporting information, but it is not the primary success metric.
The project must use deliberately seeded bugs or mutations to evaluate effectiveness, not coverage alone.
---
# 10. Langfuse Observability
Location:
src/meridian/observability/
Main client:
langfuse_client.py
Requirements:
•	One trace per module run.
•	One span per relevant workflow node or execution stage.
•	Track agent and tool execution.
•	Track LLM input and output token usage where available.
•	Track cost in USD for LLM calls.
•	Track latency and execution duration.
•	Track retries.
•	Track errors and failures.
•	Track approval outcomes.
Suggested span names:
•	comprehension
•	generation
•	test_execution
•	diagnosis
•	quality_check
•	mutation_testing
•	report
•	human_approval
Deterministic nodes do not consume LLM tokens. Record their execution time and other relevant metadata without inventing token usage.
All module runs must be traceable.
---
# 11. Memory Architecture
Location:
src/meridian/memory/
Use:
•	working_memory.py — Current module execution context.
•	long_term_memory.py — Retrieval and storage of useful historical module information.
•	sqlite_store.py — SQLite database operations.
•	checkpointing.py — LangGraph checkpoint integration.
Requirements:
•	LangGraph state holds active execution context.
•	SQLite stores approved long-term memory.
•	Store useful historical test outcomes, module summaries, confirmed conventions, and relevant execution metadata.
•	Avoid storing secrets or unnecessary source data.
•	Keep memory access controlled and auditable.
**SQLite is the required long-term memory store. Do not introduce Supabase or PostgreSQL for memory.**
LangGraph checkpointing and long-term memory are related but distinct responsibilities. Do not assume they are interchangeable.
---
# 12. MCP Integration
Location:
src/meridian/mcp/
Provide controlled tools for:
•	read_file
•	list_symbols
•	read_docstrings
•	Approved repository inspection
•	Approved test execution interactions where appropriate
Requirements:
•	Read-only repository access for source analysis.
•	No unrestricted filesystem access.
•	No production database access.
•	Validate paths and requests.
•	Prevent path traversal.
•	Log tool calls.
•	Give each agent only the tools it requires.
MCP tools must not permit agents to modify production source files.
---
# 13. Root Docker Compose Configuration
The project must have:
docker-compose.yml
at the repository root, alongside:
•	.env.example
•	AGENTS.md
•	README.md
The root Compose configuration should coordinate the required services:
•	app
•	test-runner
•	langfuse
•	mcp-server
Use the appropriate Dockerfiles and configurations.
Supporting Docker files may remain under:
infrastructure/docker/
Do not create multiple conflicting Compose configurations without an explicit reason.
---
# 14. Project Folder Structure
Maintain this structure unless an approved architecture change requires otherwise:
Meridian_testing/
│
├── .opencode/
│   ├── agents/
│   └── skills/
│
├── docs/
│   ├── client-brief.pdf
│   ├── repository-inspection.pdf
│   ├── proposed-modules.pdf
│   ├── architecture.md
│   ├── requirements-traceability.md
│   ├── implementation-plan.md
│   └── adr/
│
├── src/
│   └── meridian/
│       ├── interfaces/
│       │   ├── cli.py
│       │   └── web.py
│       │
│       ├── orchestrator/
│       │   ├── graph.py
│       │   ├── state.py
│       │   ├── nodes.py
│       │   ├── routing.py
│       │   └── approval.py
│       │
│       ├── agents/
│       │   ├── code_understanding.py
│       │   ├── test_generation.py
│       │   ├── failure_diagnosis.py
│       │   └── report_generation.py
│       │
│       ├── analysis/
│       │   ├── ast_analyzer.py
│       │   └── dependency_analyzer.py
│       │
│       ├── testing/
│       │   ├── test_runner_client.py
│       │   ├── assertion_checker.py
│       │   └── mutation_testing.py
│       │
│       ├── test_runner/
│       │   ├── Dockerfile
│       │   ├── server.py
│       │   ├── runner.py
│       │   └── requirements.txt
│       │
│       ├── tools/
│       │   ├── repository_tools.py
│       │   ├── filesystem_tools.py
│       │   ├── test_tools.py
│       │   └── github_tools.py
│       │
│       ├── mcp/
│       │   ├── server.py
│       │   └── tool_registry.py
│       │
│       ├── memory/
│       │   ├── working_memory.py
│       │   ├── long_term_memory.py
│       │   ├── sqlite_store.py
│       │   └── checkpointing.py
│       │
│       ├── observability/
│       │   ├── langfuse_client.py
│       │   └── tracing.py
│       │
│       ├── security/
│       │   ├── permissions.py
│       │   ├── validation.py
│       │   └── sandbox.py
│       │
│       └── config/
│           └── settings.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── evaluation/
│   ├── security/
│   └── fixtures/
│
├── evaluation/
│   ├── benchmark_modules/
│   ├── seeded_mutations/
│   ├── evaluation_results/
│   └── benchmark_config.yaml
│
├── infrastructure/
│   ├── docker/
│   └── github/
│       └── workflows/
│           └── regression-tests.yml
│
├── reports/
│   ├── generated/
│   └── evaluation/
│
├── scripts/
│   ├── setup.sh
│   └── run_evaluation.py
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── AGENTS.md
├── progress.md              # Session progress log — update at end of every session
├── README.md
├── pyproject.toml
└── uv.lock
This is the intended architecture, not permission to create every file immediately. Only create files when they are needed for the approved implementation phase.
---
# 15. Definition of Done
The project is complete when:
1.	Twenty named target modules have engineer-reviewed and merged tests.
2.	Mutation catch rate is measured and reported.
3.	No generated tests pass while asserting nothing meaningful.
4.	Repeated runs on unchanged code produce stable, comparable results.
5.	Each module completes within the 10-minute execution target.
6.	Cost per module and average retry count are reported.
7.	Human approval is enforced before merging.
8.	Execution is reproducible through the documented Docker setup.
9.	Langfuse traces provide visibility into every module run.
10.	Evaluation results and operational documentation are available.
The target module list must be verified against the actual repository and client requirements. Do not invent or assume the twenty modules.
---
# 16. Evaluation and Operational Requirements
The project must also include:
•	Requirements traceability.
•	Architecture Decision Records (ADRs).
•	Evaluation report.
•	Langfuse dashboard.
•	Cost model.
•	Commercial proposal.
•	Load and concurrency testing.
•	Latency p95 and p99 measurements.
•	Human escalation behavior.
•	Audit trail and approval controls.
•	Operations runbook.
•	Reproducible containerized delivery.
•	Demonstrations of failure handling:
o	Test-runner/tool unavailable.
o	Malformed input.
o	Context budget exceeded.
o	Execution timeout.
o	Invalid generated tests.
o	Likely genuine module defect.
Git history must show meaningful contributions from team members.
---
# 17. Out of Scope
Do not implement:
•	Voice or audio interfaces.
•	Production code modifications.
•	Production code refactoring.
•	Autonomous production deployments.
•	Production database access.
•	General-purpose autonomous tool building.
•	Supabase or PostgreSQL for long-term memory.
This system generates and evaluates tests. It does not autonomously repair production code.
---
# 18. Budget and Execution Constraints
•	Monthly budget: USD 400.
•	Maximum module execution time: 10 minutes.
•	Maximum diagnosis refinement cycles: 5.
•	Configurable quality-loop safety limit.
•	LLM temperature: 0.2 for generation and diagnosis.
•	Track actual LLM costs and execution costs.
•	Avoid unnecessary repeated LLM calls.
•	Keep prompts and module context within configured token budgets.
---
# 19. OpenCode and Subagent Rules
All OpenCode agents and subagents must:
1.	Read this file before implementation.
2.	Read relevant architecture and client documents.
3.	Follow the approved architecture.
4.	Avoid modifying files outside their assigned scope.
5.	Avoid simultaneous edits to shared files.
6.	Explain major dependencies and design decisions.
7.	Write tests for implemented functionality.
8.	Run relevant checks before reporting completion.
9.	Report changed files and verification results.
10.	Ask the project owner before major architectural changes.
The Architect may recommend changes but must not implement an unapproved redesign.
The Code Reviewer must check:
•	Architecture compliance.
•	Security boundaries.
•	Test quality.
•	Error handling.
•	Resource limits.
•	Human approval enforcement.
•	Observability.
•	Reproducibility.
---
# 20. Implementation Discipline
**Do not build the entire project in one uncontrolled coding operation.**
Work in small, reviewable phases.
Before each phase:
1.	Explain the objective.
2.	Identify files to create or modify.
3.	Explain dependencies.
4.	Identify security and architectural risks.
5.	State how the work will be tested.
After each phase:
1.	Summarize changes.
2.	List files changed.
3.	Show tests and verification results.
4.	Identify incomplete work.
5.	Wait for project-owner approval before proceeding to the next major phase.
Do not claim a feature is complete unless it has been implemented and verified.
**The project owner has final authority over architecture, scope, and implementation approval.**


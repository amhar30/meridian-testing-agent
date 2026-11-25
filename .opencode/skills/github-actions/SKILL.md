---
name: github-actions
description: Use when editing Meridian CI workflows in infrastructure/github/workflows/regression-tests.yml or PR validation and evaluation automation.
---

# GitHub Actions in Meridian

Read AGENTS.md §16 and docs/architecture.md §14 before changing CI.

## Workflow
- Primary workflow: `infrastructure/github/workflows/regression-tests.yml`.
- Run lint/tests, project tests, and relevant evaluation checks on pull requests.
- Use Docker Compose to reproduce the documented containerized setup where practical.
- Pin actions to immutable versions and cache dependencies deliberately.
- Keep workflow secrets in GitHub Secrets; never echo credentials or generated reports containing them.

## Constraints
- CI must not autonomously merge; human approval is required before merge (AGENTS.md §7).
- Do not expose LLM keys or production credentials to untrusted test execution.
- Keep test-runner sandbox isolation identical in CI and local Compose.
- Limit workflow runtime; module runs must respect the 10-minute target.
- Upload evaluation results and reports as artifacts for review.
- Record model, commit SHA, Python version, image digest, and config hash for reproducibility.

## Verify
- Validate YAML syntax and run the workflow on a branch before merging.
- Confirm failures surface actionable logs without leaking secrets.

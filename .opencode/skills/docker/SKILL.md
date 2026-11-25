---
name: docker
description: Use when editing Meridian's Dockerfiles, docker-compose.yml, or test-runner container isolation and security limits.
---

# Docker in Meridian

Read AGENTS.md §8 and docs/architecture.md §7 before changing containers.

## Compose
- Root `docker-compose.yml` coordinates four services: `app`, `test-runner`, `langfuse`, `mcp-server`.
- `app`: FastAPI, LangGraph, agents, MCP clients, Langfuse, SQLite access.
- `test-runner`: minimal Python image exposing `POST /run-tests`; coordinates isolated execution.
- `mcp-server`: read-only repository mount; no unrestricted filesystem.
- Keep supporting Dockerfiles under `infrastructure/docker/` and `src/meridian/test_runner/Dockerfile`.

## Test Isolation
- Untrusted generated tests get no internet, no production/LLM credentials, no Docker socket, no privileged mode.
- Read-only access to required source; writable temp workspace only; clean up afterward.
- Enforce CPU, memory, process, and wall-clock limits; reserve time inside the 10-minute module deadline.
- `server.py` must not run untrusted pytest in-process; `runner.py` launches a restricted subprocess.
- Validate and authenticate requests between `app` and `test-runner`.
- Never weaken isolation to make a test pass.

## Reproducibility
- Pin base image versions and dependency files; record image digests in evaluation results.
- Verify with `docker compose config` and a clean `docker compose up --build` before reporting done.

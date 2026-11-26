
# ADR-001: Sandbox Architecture for Test Execution

**Status:** Accepted  
**Date:** 2026-11-25  
**Author:** architect

---

## Context

Generated tests must execute in an isolated environment to prevent:

- Escape from the sandbox into the host system
- Access to LLM API keys or production secrets
- Modification of the original source repository
- Unbounded resource consumption (CPU, memory, time)

The initial folder structure referenced `runner.py` executing tests via subprocess, which is insufficient. A subprocess running inside the main app process inherits the app's environment, credentials, and filesystem access — it cannot be treated as a security boundary.

## Decision

Test execution uses a dedicated Docker-in-Docker (DinD) architecture:

1. A `dind` sidecar container runs the Docker daemon. It does NOT use the host Docker socket. This is an approved infrastructure exception and the fourth Compose service alongside the three permanent application services: `app`, `test-runner`, and `mcp-server`. It is not an application service.
2. The `dind` sidecar requires `privileged: true` to run a nested Docker daemon. This is the only container permitted to run privileged. The `test-runner` and all disposable child containers must NOT be privileged.
3. The `test-runner` container connects to the DinD daemon via the Docker API over a dedicated internal Compose network (`sandbox-net`). The connection uses mutual TLS (mTLS) over `tcp://dind:2376`. No Unix socket volume is shared between containers. The `DOCKER_HOST` environment variable in `test-runner` must point to this TLS endpoint only. The DinD API port must not be published to the host. Using unencrypted port `2375` is prohibited unless the architect explicitly approves and documents the risk.
4. `runner.py` inside `test-runner` launches a fresh disposable child container via the DinD API for each evaluation, copies isolated test files in, runs pytest, captures JSON output via `pytest-json-report`, and destroys the container unconditionally.
5. The host Docker socket (`/var/run/docker.sock`) is never mounted into `test-runner` or any application container.

### DinD Security Boundary

The privileged DinD container is a trusted infrastructure component with substantial host-kernel access. It must be treated as high-risk infrastructure.

- Never expose the DinD Docker API outside the dedicated `sandbox-net` internal network.
- Only `test-runner` may communicate with the DinD daemon. No other service may access `sandbox-net`.
- Configure the DinD Docker API to require mutual TLS client authentication.
- Only trusted `runner.py` code may interact with the Docker API.
- Use an explicit allowlist of permitted Docker operations and child-container configuration.
- Reject arbitrary Docker API parameters originating from user requests or generated test content.
- Never expose Docker client certificates, private keys, or other DinD credentials to generated tests or child containers.
- Disposable child containers must never receive access to the DinD API or Docker socket.
- Never pass host filesystem paths or sensitive host resources into child containers.
- Never expose the DinD daemon to the host network or any external interface.
- Treat compromise of the DinD container as a critical security incident.

The test-runner must store and access its Docker client certificates through a restricted, read-only location. Credentials must not appear in logs, test results, generated tests, or child-container environments.

### Child Container Security Constraints

Each disposable test execution container must have:

- No internet access (`--network none`)
- No LLM API keys or application secrets
- No Docker socket or Docker API credentials
- No privileged mode
- CPU limit: 1 core
- Memory limit: 512MB
- PID limit: 64
- Execution time limit: 7 minutes, configurable via environment variable
- Unique identity and temporary directory per run
- Docker labels identifying the evaluation run ID and runner instance ID
- Unconditional cleanup after success, failure, timeout, or runner termination, with stale-container recovery on the next startup

### Child Container Filesystem Layout

Each child container receives two distinct mounts:

- **Isolated source copy** — mounted read-only. This is a temporary copy of the target module, never the original repository.
- **Generated tests** — provided through a separate controlled temporary location (e.g. `/tmp/tests/`), writable only during setup before execution begins.
- pytest may write output only to designated temporary output locations (e.g. `/tmp/results/`).
- The original repository is never mounted into child containers.
- No path from the child container should provide access to the original repository, application credentials, Docker API credentials, or unrelated host resources.

### Test-Runner Instance Policy

The initial implementation supports exactly one active test-runner instance.

- The test-runner service must run with one replica.
- Docker Compose scaling and multiple test-runner replicas are out of scope.
- Each test-runner process must have a unique `runner_instance_id`.
- Each evaluation must have a unique `meridian.run_id`.
- Every child container must carry both labels:
  - `meridian.run_id=<uuid>`
  - `meridian.runner_instance_id=<uuid>`
- The trusted test-runner process maintains an active-evaluation registry.
- The test-runner must never remove containers belonging to active evaluations.
- Multi-instance execution requires a revised ADR defining distributed ownership, leases or heartbeats, and safe cross-instance cleanup.

### Orphan Container Cleanup

If `test-runner` crashes or is killed, its Python cleanup code cannot execute. To handle this:

- Every sandbox container is created with the labels `meridian.run_id=<uuid>` and `meridian.runner_instance_id=<uuid>`.
- On test-runner startup, `runner.py` queries the DinD daemon for containers bearing the Meridian labels.
- It identifies stale containers left by previous runner processes.
- It removes only containers confirmed to be stale and not belonging to an active evaluation.
- Startup cleanup must complete before accepting new evaluation requests.
- Cleanup must be bounded and must never remove containers associated with an active evaluation.
- Cleanup failures must be logged and reported as operational errors.

The single-runner restriction is important: the initial design does not support distributed cleanup across multiple runner instances.

## Alternatives Considered

### Option A: Subprocess only

Run pytest in a subprocess from within the main app.

**Rejected because:** subprocess inherits the parent process environment, filesystem access, and credentials. It is not a security boundary.

### Option B: Host Docker socket

Mount `/var/run/docker.sock` into the test-runner container.

**Rejected because:** access to the host socket grants full Docker daemon control, potentially equivalent to root on the host. This breaks the intended isolation boundary.

### Option C: gVisor / Kata Containers

Use a kernel-level sandbox runtime.

**Rejected because:** adds significant infrastructure complexity and expertise requirements. DinD is selected for this project's scope, with its residual risks explicitly acknowledged.

### Option D: Shared Unix Socket Volume Between test-runner and dind

Share the DinD socket as a Docker volume mount into `test-runner`.

**Rejected because:** a shared socket volume is harder to audit and restrict than a network API endpoint. Using a dedicated internal network with an explicit `DOCKER_HOST` endpoint makes the access boundary explicit and auditable.

## Assumptions

- The deployment environment supports Docker-in-Docker and the privileged sidecar is not blocked by host kernel policy.
- The bootcamp evaluation environment allows a privileged `dind` sidecar.
- The initial deployment supports a single test-runner instance.
- The test-runner can securely obtain and use the required mutual TLS client certificates.
- The infrastructure-engineer provides the approved offline dependency-provisioning mechanism for the testing-engineer.

Rootless DinD may be investigated if the environment does not permit privileged mode. However, it must not be introduced as an undocumented replacement. The architect must evaluate the compatibility and security implications and record an ADR update before implementation.

## Offline Dependency Provisioning

The infrastructure-engineer owns the approved offline dependency-provisioning mechanism.

- The infrastructure-engineer defines the wheelhouse or approved dependency bundle location.
- The infrastructure-engineer configures access to the bundle for the test-runner.
- The testing-engineer identifies required Python packages and pinned versions.
- The testing-engineer consumes the approved dependency bundle.
- Dependencies must be available without unrestricted internet access from child containers.
- Dependency versions and relevant hashes must be recorded for reproducibility.
- Any change to the dependency-provisioning mechanism requires coordination between the two agents.

The testing-engineer must not introduce a separate dependency-distribution architecture without approval.

## If DinD Is Unavailable

If DinD is unavailable or blocked in the target environment, implementation must stop.

- The architect must evaluate and approve an alternative sandbox architecture.
- The host Docker socket must never be introduced as a workaround.
- No fallback may be implemented without explicit approval.
- Do not substitute an unrestricted subprocess, a host-mounted socket, or any mechanism that weakens the approved security boundary.

## Consequences

### Positive

- Generated tests execute in disposable child containers.
- The original repository remains read-only and is never mounted directly into child containers.
- Child containers have restricted networking, resources, filesystem access, and privileges.
- Docker API access is restricted to trusted test-runner code through mutual TLS.
- Container resource limits are enforceable.
- DinD API access is restricted through a dedicated internal network.
- Cleanup mechanisms reduce the risk of abandoned containers.

### Negative / Trade-offs

- DinD adds container startup latency (approximately 1–3 seconds per evaluation, subject to actual measurement).
- DinD configuration is more complex than a simple subprocess.
- Requires a privileged sidecar.
- TLS certificate configuration and management add setup overhead.
- Offline dependency provisioning adds preparation and maintenance overhead.
- The initial single-runner restriction limits horizontal scaling.

### Security Risks and Residual Limitations

This architecture provides container-level isolation. It does NOT provide VM-grade isolation or guarantee absolute separation from the host.

- The privileged DinD service has substantial access to the host kernel.
- Child containers share the host kernel through the nested Docker daemon.
- The trusted test-runner has powerful control over the nested Docker daemon through its API.
- A compromise of DinD or a relevant kernel/container-runtime vulnerability could undermine the intended isolation.
- Container isolation reduces the attack surface but does not eliminate shared-kernel risks.

DinD must therefore be treated as trusted, high-risk infrastructure. Only trusted test-runner code may access its API, and generated test code must never receive Docker API credentials or access.

If the deployment environment cannot support the approved DinD design, work stops until the architect approves a revised architecture.

## Verification

The following requirements must be verified through actual execution evidence:

### Service and API Security

- `docker compose up` starts all containers including the `dind` sidecar.
- Confirm only `test-runner` can reach the DinD Docker API.
- Confirm no other service is connected to `sandbox-net`.
- Confirm the DinD API requires mutual TLS client authentication.
- Confirm `DOCKER_HOST` uses `tcp://dind:2376`.
- Confirm the DinD API port is not published to the host.
- Confirm no Unix socket volume is shared between `test-runner` and `dind`.
- Confirm the host Docker socket is not mounted into any application container.
- Confirm Docker client certificates and private keys are not exposed to generated tests or child containers.
- Confirm only trusted runner code can issue Docker API requests.

### Child Container Isolation

- Confirm disposable child containers cannot access the DinD Docker API or socket.
- Confirm child containers cannot access host filesystem paths.
- Confirm child containers receive no application, LLM, or Docker API secrets.
- Confirm resource limits (CPU, memory, PID, and time) are enforced on actual child containers.
- Confirm child containers use `--network none`.
- Confirm the DinD daemon is not exposed outside `sandbox-net`.
- Confirm the test-runner cannot reach unrestricted external internet destinations.
- Confirm child containers cannot reach external internet destinations.
- Confirm network tests fail because of actual network isolation, not because of missing utilities or unrelated errors.

### Filesystem and Test Execution

- Confirm the original source repository volume is read-only inside `test-runner`.
- Confirm child containers receive the isolated source copy read-only.
- Confirm generated tests are provided in a separate controlled location.
- Confirm pytest output is written only to designated temporary locations.
- Confirm the original repository remains unchanged after test execution.
- Confirm a timed-out evaluation destroys its child container completely.

### Runner and Cleanup

- Confirm the test-runner runs as a single instance.
- Confirm each runner process has a unique `runner_instance_id`.
- Confirm each evaluation has a unique `meridian.run_id`.
- Confirm child containers carry both required labels.
- Confirm cleanup occurs after success, failure, timeout, and cancellation.
- Confirm a simulated unexpected test-runner crash leaves stale containers that are removed on the next startup.
- Confirm startup cleanup does not remove containers belonging to active evaluations.
- Confirm cleanup failures are reported.

### Dependency Provisioning

- Confirm required dependencies are available through the approved offline bundle.
- Confirm child containers do not require unrestricted internet access to install packages.
- Confirm dependency versions and hashes are recorded.
- Confirm missing dependencies produce a clear failure.

Requirements that have only been documented or configured but not tested must be reported as NOT VERIFIED, not PASS.

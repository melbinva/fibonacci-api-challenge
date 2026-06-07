# Fibonacci Sequence API

This project implements a REST API that returns the nth Fibonacci number.

## Tech Stack

- Python 3.12
- FastAPI
- Pytest
- Docker
- GitHub Actions

## Endpoints

Base URL (local): `http://127.0.0.1:8000`

Quick reference:

- `GET /` -> landing page
- `GET /health` -> health check
- `GET /fibonacci?n=<integer>` -> nth Fibonacci value
- `GET /openapi.json` -> OpenAPI spec
- `GET /docs` -> Swagger UI
- `GET /swagger` -> alias to Swagger UI (`/docs`)

### Health Endpoint

Request:

```bash
curl -s http://127.0.0.1:8000/health
```

Response:

{
  "status": "ok"
}

### Fibonacci Endpoint

Request:

```bash
curl -s "http://127.0.0.1:8000/fibonacci?n=10"
```

Response:

{
  "n": 10,
  "value": 55
}

Validation behavior:

- n < 0 -> 400
- n missing or non-integer -> 422
- n > 100000 -> 400 (guard rail)

Failure examples:

```bash
curl -i "http://127.0.0.1:8000/fibonacci?n=-1"
curl -i "http://127.0.0.1:8000/fibonacci?n=abc"
```

## Local Run

1. Install uv (one time):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and sync the environment:

```bash
uv sync --all-groups
```

### Virtual Environment (venv) Note

- `uv sync` creates and manages a project virtual environment at `.venv/`.
- You can run commands directly without activating venv:
  - `uv run uvicorn src.app.main:app --reload`
  - `uv run pytest -q`
- If you prefer activation-based workflow:
  - `source .venv/bin/activate`
  - then run tools normally (for example, `python`, `pytest`, `uvicorn`).

3. Start the API:

```bash
uv run uvicorn src.app.main:app --reload
```

4. Open:

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Example: http://127.0.0.1:8000/fibonacci?n=10

## Run Tests

```bash
uv run pytest -q
```

## Docker

Security requirement: always keep least-privilege runtime guidance in this document.

Build image (least-privilege by default in this Dockerfile):

```bash
docker build -t fibonacci-api .
```

Run container:

```bash
docker run --rm -p 8000:8000 fibonacci-api
```

Verify container user is non-root:

```bash
docker run --rm --entrypoint id fibonacci-api:least-priv
```

## Kubernetes (Production Manifests)

Production-ready manifests are available in [k8s](k8s):

- [k8s/deployment.yaml](k8s/deployment.yaml)
- [k8s/service.yaml](k8s/service.yaml)
- [k8s/hpa.yaml](k8s/hpa.yaml)
- [k8s/ingress.yaml](k8s/ingress.yaml)
- [k8s/pdb.yaml](k8s/pdb.yaml)
- [k8s/serviceaccount.yaml](k8s/serviceaccount.yaml)
- [k8s/networkpolicy.yaml](k8s/networkpolicy.yaml)
- [k8s/kustomization.yaml](k8s/kustomization.yaml)

Before applying:

1. Replace image in [k8s/deployment.yaml](k8s/deployment.yaml) with your ACR image, for example:
  `myregistry.azurecr.io/fibonacci-api:latest`
2. Replace ingress host in [k8s/ingress.yaml](k8s/ingress.yaml) with your domain.
3. Replace TLS secret name in [k8s/ingress.yaml](k8s/ingress.yaml) with your certificate secret.
4. Ensure your cluster can pull from ACR (for AKS, use `az aks update --attach-acr`).

Deploy with:

```bash
kubectl apply -k k8s
```

Check rollout:

```bash
kubectl -n fibonacci-prod rollout status deploy/fibonacci-api
```

SRE best-practice hardening included:

- Rolling updates with `maxUnavailable: 0`, `minReadySeconds`, and rollout deadline.
- Startup, readiness, and liveness probes.
- Non-root runtime, dropped Linux capabilities, read-only root filesystem.
- Topology spread and anti-affinity for better availability.
- PodDisruptionBudget and autoscaling behavior tuning to reduce flapping.
- NetworkPolicy to restrict inbound traffic to app pods.

Optional SRE observability resources (Prometheus Operator required):

- [k8s/monitoring/servicemonitor.yaml](k8s/monitoring/servicemonitor.yaml)
- [k8s/monitoring/prometheusrule.yaml](k8s/monitoring/prometheusrule.yaml)
- [k8s/monitoring/kustomization.yaml](k8s/monitoring/kustomization.yaml)

Apply monitoring resources:

```bash
kubectl apply -k k8s/monitoring
```

Notes:

- These resources require the `ServiceMonitor` and `PrometheusRule` CRDs (usually from kube-prometheus-stack).
- Update the `release` label in monitoring manifests if your Prometheus stack uses a different selector.

## Production Deployment Considerations

### Containerization

- Package as a Docker image and deploy to a container runtime.
- Keep image minimal using python:slim.
- Run as a non-root user in the container (least privilege).
- Preserve this least-privilege requirement in future README updates.

### CI/CD

- GitHub Actions workflow is included in .github/workflows/ci.yml.
- Workflows are configured to run on self-hosted Linux runners (not `ubuntu-latest`).
- On pull requests and pushes:
  - install dependencies
  - run tests
  - build Docker image
- Typical production extension:
  - push image to Azure Container Registry (ACR)
  - deploy to Azure Kubernetes Service (AKS)

Base production CD template and variable files are included:

- `.github/workflows/cd-template.yml`
- `.github/variables.example.env`
- `.github/secrets.example.env`

The template is Azure-only and uses:

- GitHub OIDC federated identity login to Azure (no client secret by default)
- AKS managed identity attachment to ACR for image pull (`az aks update --attach-acr`)

Passwordless authentication (recommended):

- Use GitHub OIDC federation with Microsoft Entra ID for workflow authentication.
- Do not store long-lived Azure passwords or client secrets in repository secrets when OIDC is available.
- Configure Azure login with:
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`
- This enables short-lived, workload-issued tokens and reduces secret exposure risk.

Self-hosted runner prerequisites:

- `docker`
- `python` 3.12
- `uv`
- `az` CLI
- `kubectl` (required for AKS deployment workflow)

Template usage:

```bash
# 1) create repo variables and secrets from example files
# .github/variables.example.env
# .github/secrets.example.env

# 2) enable and run the template workflow
# GitHub Actions -> "CD Template" -> Run workflow
```

### Monitoring and Logging

- Request logging middleware records method, path, status code, and latency.
- In production, ship logs to a centralized platform (CloudWatch, Datadog, ELK, Azure Monitor).
- Add metrics such as request rate, p95 latency, error rate, and saturation.

### Scaling Strategy

- Service is stateless and horizontally scalable.
- Run multiple replicas behind a load balancer.
- Use autoscaling based on CPU and request rate.
- Add rate limiting and caching where appropriate to protect service under load.

## Algorithm Choice

- Implemented iterative Fibonacci, not recursive.
- Complexity:
  - Time: O(n)
  - Space: O(1)

## AI Usage

Per interview guidance, AI assistance was used and reviewed critically.

### Where AI was used

- Initial FastAPI scaffold (app structure, route scaffolding, test skeleton).
- Refactoring support for module organization (`src/app/helper/*`, router separation, app factory).
- Drafting operational documentation sections in this README.

### How AI was used

- Used AI for iterative suggestions, not one-shot generation.
- Reviewed each suggestion before applying, then adjusted code to match project requirements.
- Used AI mainly for speed on boilerplate and refactor patterns; business logic decisions were manually verified.

### What was accepted vs modified

- Accepted:
  - Base FastAPI endpoint scaffolding.
  - Initial test structure and containerization/docs boilerplate.
- Modified:
  - Error handling to use a consistent custom JSON error envelope.
  - Route organization into dedicated modules and helper package.
  - App bootstrap into `create_app()` factory pattern.
  - Swagger/ReDoc configuration (kept Swagger, disabled ReDoc for challenge usage).
  - Tests updated to match final error-response contract.

### How correctness was validated

- Automated tests: `uv run pytest -q` (all tests passing).
- Manual endpoint verification for:
  - Success cases (`/health`, `/fibonacci?n=0`, `/fibonacci?n=10`)
  - Failure cases (`n < 0`, `n` missing, invalid `n`, over max limit)
- Static error checks in edited modules during refactoring.

### What AI got wrong or incomplete

- Earlier generated tests expected FastAPI default error shape (`detail`) after custom handlers were introduced.
- A stale `/redoc` link remained after disabling ReDoc and required manual correction.
- Initial drafts did not fully align with final structure goals (helper package + app factory), so additional manual refactoring was required.

## Evaluation Criteria Coverage

- Functionality of the API:
  - Implements `GET /fibonacci?n=<integer>` with deterministic Fibonacci output.
  - Provides `GET /health` for service health checks.
  - Includes input validation and guardrails for negative, missing, invalid, and oversized `n` values.
- Clarity and quality of the code:
  - Uses `src/`-root modular structure with clear separation of concerns (`router`, `constants`, `helper`).
  - Applies consistent custom error handling and request logging through dedicated helper modules.
  - Keeps app initialization centralized in `create_app()` for maintainability and testability.
- Completeness and clarity of the documentation:
  - Documents endpoints, local run steps, testing, container usage, and Kubernetes deployment.
  - Includes API behavior examples for success and failure cases.
  - Includes explicit AI-usage disclosure and validation notes.
- Consideration of operational and deployment aspects:
  - Provides Docker image build/run instructions and CI workflow configuration.
  - Includes production-focused Kubernetes manifests (deployment, service, ingress, HPA, PDB, network policy).
  - Covers operational concerns such as readiness/liveness checks, scaling, logging, and monitoring.



# Fibonacci Sequence API

This project implements a REST API that returns the nth Fibonacci number.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Endpoints](#endpoints)
- [Local Run](#local-run)
- [Run Tests](#run-tests)
- [Docker](#docker)
- [Kubernetes (Production Manifests)](#kubernetes-production-manifests)
- [Production Deployment Considerations](#production-deployment-considerations)
- [Algorithm Choice](#algorithm-choice)
- [AI Usage](#ai-usage)
- [Evaluation Criteria Coverage](#evaluation-criteria-coverage)

## Tech Stack

[Back to Table of Contents](#table-of-contents)

- Python 3.12
- FastAPI
- Pytest
- Docker
- GitHub Actions

## Endpoints

[Back to Table of Contents](#table-of-contents)

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

[Back to Table of Contents](#table-of-contents)

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

[Back to Table of Contents](#table-of-contents)

```bash
uv run pytest -q
```

## Docker

[Back to Table of Contents](#table-of-contents)

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
docker run --rm --entrypoint id fibonacci-api
```

## Kubernetes (Production Manifests)

[Back to Table of Contents](#table-of-contents)

Production-ready manifests are available in [k8s](k8s):

- [k8s/deployment.yaml](k8s/deployment.yaml)
- [k8s/service.yaml](k8s/service.yaml)
- [k8s/hpa.yaml](k8s/hpa.yaml)
- [k8s/ingress.yaml](k8s/ingress.yaml)
- [k8s/pdb.yaml](k8s/pdb.yaml)
- [k8s/serviceaccount.yaml](k8s/serviceaccount.yaml)
- [k8s/secretproviderclass.yaml](k8s/secretproviderclass.yaml)
- [k8s/networkpolicy.yaml](k8s/networkpolicy.yaml)
- [k8s/kustomization.yaml](k8s/kustomization.yaml)

Before applying:

1. For pipeline-driven deployments, no manual image edit is required. The image reference in [k8s/deployment.yaml](k8s/deployment.yaml) is rendered from GitHub variables (`REGISTRY_HOST` and `IMAGE_NAME`) during stage-specific manifest rendering.
2. Set deployment template values through GitHub Actions variables using:
  - [.github/variables.common.env.schema](.github/variables.common.env.schema)
  - [.github/variables.dev.env.schema](.github/variables.dev.env.schema)
  - [.github/variables.test.env.schema](.github/variables.test.env.schema)
  - [.github/variables.prod.env.schema](.github/variables.prod.env.schema)
3. The CD pipeline renders those variables into the Kubernetes templates before applying them.
4. Ensure AKS has Secrets Store CSI Driver + Azure Key Vault provider installed and workload identity enabled.
5. Ensure your cluster can pull from ACR (for AKS, use `az aks update --attach-acr`).

Important:

- The Kubernetes manifests in [k8s](k8s) contain template placeholders (for example `${REGISTRY_HOST}`, `${INGRESS_HOST}`, and identity/key vault variables).
- Do not run `kubectl apply -k k8s` directly unless placeholders are rendered or replaced first.
- Recommended path: use the CD workflow, which renders templates before applying them.

TLS note:

- [k8s/ingress.yaml](k8s/ingress.yaml) references `secretName: fibonacci-api-tls`.
- That secret is synced from Azure Key Vault by [k8s/secretproviderclass.yaml](k8s/secretproviderclass.yaml) when the deployment mounts the CSI volume.

Deploy with (after rendering templates):

```bash
kubectl apply -k rendered-k8s-<stage>
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

[Back to Table of Contents](#table-of-contents)

Scope boundary:

- This repository is intentionally focused on application workload delivery (build, test, containerize, deploy application manifests).
- Infrastructure provisioning and lifecycle management should be handled in a separate repository using Infrastructure as Code, preferably Terraform.

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
  - run Kubernetes manifest what-if validation (kustomize render + client dry-run)
  - build Docker image
- Typical production extension:
  - push image to Azure Container Registry (ACR)
  - deploy to Azure Kubernetes Service (AKS)

Base production CD template and variable files are included:

- `.github/workflows/cd-template.yml`
- `.github/variables.common.env.schema`
- `.github/variables.dev.env.schema`
- `.github/variables.test.env.schema`
- `.github/variables.prod.env.schema`
- `.github/secrets.env.schema`

The template is Azure-only and uses:

- GitHub OIDC federated identity login to Azure for both CI image push and CD deployment (no client secret by default)
- stage-based deployment flow: `dev` -> `test` -> production approval -> `prod`
- non-production ACR for `dev` and `test`, production ACR for `prod`
- AKS managed identity attachment to ACR for image pull (`az aks update --attach-acr`)
- GitHub Environment-based stage controls (`DEV_DEPLOYMENT_ENVIRONMENT`, `TEST_DEPLOYMENT_ENVIRONMENT`, `PROD_DEPLOYMENT_ENVIRONMENT`)
- Post-deployment validation per stage (cluster checks + optional HTTP health checks via `DEV_AKS_VALIDATION_URL`, `TEST_AKS_VALIDATION_URL`, `PROD_AKS_VALIDATION_URL`)
- Pipeline-based manifest template rendering from GitHub variables before `kubectl apply`

Stage namespace note:

- Current base manifests are pinned to `fibonacci-prod` namespace in [k8s/kustomization.yaml](k8s/kustomization.yaml).
- Keep `DEV_AKS_NAMESPACE`, `TEST_AKS_NAMESPACE`, and `PROD_AKS_NAMESPACE` aligned with rendered manifest namespace values, or template the namespace field as a future enhancement.

Passwordless authentication (recommended):

- Both the CI workflow and CD template use GitHub OIDC federation with Microsoft Entra ID for passwordless authentication.
- CI logs into Azure with `azure/login` and performs `az acr login` before pushing the image.
- Do not store long-lived Azure passwords or client secrets in repository secrets when OIDC is available.
- Configure Azure login with:
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`
- Configure ACR/image variables with:
  - `NONPROD_ACR_NAME`
  - `NONPROD_REGISTRY_HOST`
  - `PROD_ACR_NAME`
  - `PROD_REGISTRY_HOST`
  - `IMAGE_NAME`
- This enables short-lived, workload-issued tokens and reduces secret exposure risk.

Image push behavior on `main`:

- CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) pushes to non-production ACR on `main`.
- CD template ([.github/workflows/cd-template.yml](.github/workflows/cd-template.yml)) also builds and pushes to both non-production and production ACR.
- If you want a single push source of truth, disable image push in one workflow.

Self-hosted runner prerequisites:

- `docker`
- `python` 3.12
- `uv`
- `az` CLI
- `kubectl` (required for AKS deployment workflow)

Runner note:

- `uv` is installed by the CI workflow via `astral-sh/setup-uv` and does not need to be preinstalled on the runner.
- The AKS CD template specifically requires `docker`, `az`, and `kubectl` on the self-hosted runner.

Template usage:

```bash
# 1) create repository-level shared variables and optional secrets
# .github/variables.common.env.schema
# .github/secrets.env.schema

# 2) create environment-specific variables in GitHub Environments
# dev   -> .github/variables.dev.env.schema
# test  -> .github/variables.test.env.schema
# prod  -> .github/variables.prod.env.schema

# 3) enable and run the template workflow
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

[Back to Table of Contents](#table-of-contents)

- Implemented iterative Fibonacci, not recursive.
- Complexity:
  - Time: O(n)
  - Space: O(1)

## AI Usage

[Back to Table of Contents](#table-of-contents)

Per interview guidance, AI assistance was used and reviewed critically.

### Where AI was used

- Initial FastAPI scaffold (app structure, route scaffolding, Fibonacci endpoint draft, and test skeleton).
- Refactoring support for module organization (`src/app/helper/*`, router separation, app factory).
- Drafting operational documentation sections in this README.
- Sanity-checking whether the solution covered the assignment requirements, including deployment and operational considerations.

### How AI was used

- Used AI for iterative suggestions, not one-shot generation.
- Used AI as a productivity aid for first drafts and structure, not as a final source of truth.
- Treated generated output as a starting point rather than finished code.
- Reviewed each suggestion before applying, then adjusted code to match project requirements.
- Used AI mainly for speed on boilerplate and refactor patterns; business logic decisions were manually verified.

### What was accepted vs modified

- Accepted:
  - Base FastAPI endpoint scaffolding.
  - Initial test structure and containerization/docs boilerplate.
- Modified:
  - Error handling to use a consistent custom JSON error envelope.
  - The Fibonacci implementation to keep it iterative and efficient.
  - Route organization into dedicated modules and helper package.
  - App bootstrap into `create_app()` factory pattern.
  - Swagger/ReDoc configuration (kept Swagger, disabled ReDoc for challenge usage).
  - Tests updated to match final error-response contract.
  - README wording and structure.
  - Production-readiness details so they were more concrete and aligned with the assignment.

### How correctness was validated

- Automated tests: `uv run pytest -q` (all tests passing).
- Manual file-by-file review of generated code before finalizing changes.
- Manual endpoint verification for:
  - Success cases (`/health`, `/fibonacci?n=0`, `/fibonacci?n=10`)
  - Failure cases (`n < 0`, `n` missing, invalid `n`, over max limit)
- Verified Swagger/OpenAPI exposure and documentation endpoints.
- Static error checks in edited modules during refactoring.

### What AI got wrong or incomplete

- Initial AI-generated Kubernetes manifests and Docker configuration did not fully satisfy the project’s security requirements. I later revised them to follow least-privilege principles, non-root execution, and container hardening best practices.
- The original Dockerfile was not implemented as a multi-stage build, so I refactored it to reduce the runtime footprint and improve security posture.
- I added observability-related resources to improve monitoring readiness and operational visibility.
- Earlier generated tests expected FastAPI default error shape (`detail`) after custom handlers were introduced.
- A stale `/redoc` link remained after disabling ReDoc and required manual correction.
- Initial drafts did not fully align with final structure goals (helper package + app factory), so additional manual refactoring was required.

## Evaluation Criteria Coverage

[Back to Table of Contents](#table-of-contents)

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



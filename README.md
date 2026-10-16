# LabShelf

LabShelf is an original laboratory equipment inventory built for a DevOps
capstone. Add, search, filter, edit, and remove equipment while tracking quantities,
storage locations, and low-stock thresholds.

**Azure demonstration:** <http://4.224.66.52> ·
**Repository:** [ThereIsSomething/devops-final-proj](https://github.com/ThereIsSomething/devops-final-proj)

**For evaluation:** start with the [submission guide](SUBMISSION.md), then the
[numbered screenshots](docs/evidence/README.md).

The public demo is an editable classroom sandbox. Use synthetic equipment data.
The cloud demo stays running for evaluation; cleanup is a separate step.

## Architecture

```mermaid
flowchart LR
    Developer --> GitHub
    GitHub --> Actions[Tests, audits, build, scan]
    Actions --> GHCR[GHCR: commit-SHA images]
    Actions --> Desired[Git desired image version]
    Desired --> Flux
    Terraform --> AKS[Azure Kubernetes Service]
    Flux --> Helm[Helm release on AKS]
    Browser --> Traefik
    Traefik --> Frontend[React / Nginx: 2 replicas]
    Traefik --> Backend[FastAPI: 2+ replicas]
    Frontend --> Backend
    Backend --> PostgreSQL[PostgreSQL / persistent disk]
    Prometheus --> Backend
    Grafana --> Prometheus
```

Terraform provisions Azure infrastructure. Flux manages the application Helm
release. Ingress and monitoring bootstrap use versioned Helm commands and are
not represented as Flux-managed.

## Technologies

React 19, Vite 8, FastAPI, SQLAlchemy 2, PostgreSQL 17, Alembic, pytest,
Docker/Compose, GitHub Actions, GHCR, Ruff, Bandit, pip-audit, npm audit, Trivy,
Terraform, AKS, Helm, Traefik, Flux, Prometheus, and Grafana. Requirements files,
the npm lockfile, and Terraform lockfiles record package/provider selections.

## Application and Docker setup

Install Docker with a working Linux engine and Compose. In PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Open <http://localhost:3000>; API docs are at <http://localhost:8000/docs>.
Application containers use non-root users. Compose waits for database readiness,
runs migrations, and stores PostgreSQL data in a named volume. See
[local development](docs/local-development.md) for native setup and tests.

Both images built locally on Windows, HTTP and browser CRUD passed against
PostgreSQL, and all six records survived backend restart and database container
replacement. See the
[local verification report](docs/local-verification.md).

## API and tests

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness and deployed commit version |
| GET | `/ready` | Database and table readiness |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/equipment` | List with `q`, `category`, `low_stock` filters |
| GET | `/api/equipment/{id}` | Read one record |
| POST | `/api/equipment` | Create a validated record |
| PUT | `/api/equipment/{id}` | Replace editable fields |
| DELETE | `/api/equipment/{id}` | Delete a record |
| GET | `/api/summary` | Record/unit totals, low-stock count, categories |

Low stock means quantity is at or below its threshold. Text is trimmed and
required; negative, fractional, boolean, and oversized quantities are rejected.
Unknown IDs return 404. Alembic owns schema creation; startup does not call
`create_all`. PostgreSQL advisory locks serialize concurrent replica migrations.

There are 22 passing pytest cases covering CRUD, validation, filters, totals,
missing records, metrics, readiness failure, and migration up/repeat/down.
Each API test uses an isolated SQLite database. Real cloud HTTP smoke tests,
PostgreSQL queries, and disk persistence checks are recorded separately.

## CI/CD and DevSecOps

The [delivery workflow](.github/workflows/delivery.yml) runs on every push to
main, including documentation changes, and on pull requests. Lint, SAST, tests,
dependency audits, frontend build, and secret scanning gate image builds.
Trivy scans both images and fails on HIGH/CRITICAL
findings, including unfixed ones. Successful main builds publish full-SHA GHCR
tags, then commit that tested tag to the desired state read by Flux. Automated
promotion commits cannot promote themselves again.

[Successful pipeline](https://github.com/ThereIsSomething/devops-final-proj/actions/runs/38946165777)
and [scan findings](security/scan-findings.md) provide actual execution evidence.
The first backend image was blocked by its OS vulnerability scan. An Alpine
replacement passed without weakening the gate. CI holds no cluster credentials.

## Terraform

- [Azure runbook](terraform/azure/README.md): applied resource group, VNet, two
  subnets, AKS, two system nodes, and network role assignment in Central India.
  The actual nodes run Kubernetes 1.36.4.
- [AWS alternative](terraform/aws/README.md): VPC, two public and two private
  subnets, NAT, EKS managed nodes, and EBS CSI/IRSA. Init and validate completed.
  AWS plan/apply were not executed; AWS provisioning is not claimed.

The instructor approved Azure execution. AKS/VNet/node-pool evidence is the
approved substitution for EKS/VPC/node-group evidence. Azure subnets are not a
direct rename of AWS public/private subnets. State, saved plans, credentials,
and kubeconfig stay outside Git; Terraform state needs a secure backup.

## Kubernetes, Helm, monitoring, and GitOps

The [cluster runbook](docs/cluster-deployment.md) covers Secret creation, Helm,
Ingress, and monitoring access. The chart provides ConfigMap, existing Secret
references, two frontend and two or more backend replicas, probes, resource
limits, HPA, ClusterIP Services, Ingress, and persistent PostgreSQL storage.

Prometheus scrapes both backend pods. Grafana's LabShelf dashboard charts request
rate, p95 latency, request totals, and targets UP. Monitoring uses localhost port
forwards. Generate real traffic with `python scripts/load.py http://4.224.66.52`.

[Flux setup](gitops/README.md) explains reconciliation. Change visible frontend
text, commit and push, follow Actions, then compare the browser and `/health`
version after Flux updates the release. See the [demo guide](docs/presentation.md).

## Troubleshooting and lessons learned

[Isolated exercises](troubleshooting/README.md) reproduce an invalid image and
a Service selector mismatch in a separate namespace. Real deployment also
exposed initial database DNS/readiness timing and an undersized Grafana limit.
The evidence index records symptoms, investigation, fixes, and recovery.

Lessons from execution: teaching examples need validation, SQLite tests do not
prove PostgreSQL integration, image scans include OS packages, Service labels
must match ready pods, and a running container can still be unready.

This is a classroom architecture: PostgreSQL has one pod, persistent storage is
not backup, monitoring history is ephemeral, and the app has no authentication
or TLS. These limits are documented without claiming production readiness.

## Screenshots and evidence

The [submission guide](SUBMISSION.md) maps each course module to its source and
results. Open the [numbered screenshots](docs/evidence/README.md) for a visual
review, the [execution notes](docs/evidence.md) for failures and fixes, or the
[presentation guide](docs/presentation.md) for the live demonstration commands.

![LabShelf deployed on Azure](docs/evidence/screenshots/03-cloud-inventory.jpg)
![Prometheus application targets UP](docs/evidence/screenshots/17-prometheus-targets-up.jpg)
![Grafana application metrics](docs/evidence/screenshots/18-grafana-application-metrics.jpg)

Submit the repository URL linked above. Source files, setup instructions,
screenshots, and execution records are available directly in the repository.

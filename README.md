# LabShelf

LabShelf is a laboratory equipment inventory built for a DevOps course capstone.
It tracks equipment names, categories, quantities, low-stock thresholds, and
storage locations. The application is original; the instructor's TaskBoard
sample remains local reference material.

## Delivery scope

React/Vite → FastAPI → PostgreSQL, with Alembic migrations, pytest, non-root
containers, Docker Compose, GitHub Actions, GHCR, security gates, Terraform,
Kubernetes/Helm, Prometheus/Grafana, and Flux GitOps.

Azure is the approved demonstration provider. Separate AWS Terraform code will
be supplied, with validation reported independently from Azure execution.

## Status

Implementation is in progress. Cloud deployment, successful CI, container builds,
and screenshots must be supported by actual execution before they are marked
complete. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for requirements and
[docs/evidence.md](docs/evidence.md) for verified outcomes.

Cloud resources remain running until the student explicitly requests cleanup.

## Development

Backend setup instructions will be added with the first working API milestone.
Do not commit local environment files, credentials, Terraform state, or kubeconfig.

## Academic use

This project is being developed with AI assistance. Review and understand the
code and follow the course's disclosure requirements. Evidence records real
commands and results; screenshots and commit history are not fabricated.

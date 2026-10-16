# LabShelf — project evidence

Start with the [submission guide](../../SUBMISSION.md) for the grading-module
mapping. The screenshots below are numbered in presentation order.

| No. | Screenshot | What it shows |
| --- | --- | --- |
| 01 | [Local inventory](screenshots/01-local-inventory.jpg) | Six equipment records in the Compose application |
| 02 | [Mobile inventory](screenshots/02-mobile-inventory.jpg) | Responsive layout at mobile width |
| 03 | [Cloud inventory](screenshots/03-cloud-inventory.jpg) | Application accessed through the AKS Ingress after deployment |
| 04 | [API tests passing](screenshots/04-api-tests-passing.png) | All 22 tests pass |
| 05 | [Git commit history](screenshots/05-git-commit-history.png) | Meaningful application and infrastructure development commits |
| 06 | [Docker Compose running](screenshots/06-docker-compose-running.png) | Backend/frontend image builds and all three services running |
| 07 | [Delivery pipeline success](screenshots/07-delivery-pipeline-success.jpg) | Quality, both image jobs and promotion succeed |
| 08 | [Backend registry image](screenshots/08-backend-registry-image.jpg) | Published GHCR backend package and commit-SHA tag |
| 09 | [Frontend registry image](screenshots/09-frontend-registry-image.jpg) | Published GHCR frontend package and commit-SHA tag |
| 10 | [Backend security scan](screenshots/10-backend-security-scan.jpg) | Trivy report in the backend pipeline job |
| 11 | [Frontend security scan](screenshots/11-frontend-security-scan.jpg) | Trivy report in the frontend pipeline job |
| 12 | [Azure Terraform creation plan](screenshots/12-azure-terraform-creation-plan.png) | Saved original plan: six additions |
| 13 | [Azure infrastructure resources](screenshots/13-azure-infrastructure-resources.jpg) | Deployed AKS and virtual network in Central India |
| 14 | [Kubernetes workloads and Services](screenshots/14-kubernetes-workloads-and-services.png) | Running pods, Services, Ingress, HPA and persistent storage |
| 15 | [Helm release deployed](screenshots/15-helm-release-deployed.png) | Successful LabShelf Helm release |
| 16 | [API Prometheus metrics](screenshots/16-api-prometheus-metrics.png) | Handler-labelled HTTP metrics returned by the backend |
| 17 | [Prometheus targets UP](screenshots/17-prometheus-targets-up.jpg) | Both backend scrape targets are healthy |
| 18 | [Grafana application metrics](screenshots/18-grafana-application-metrics.jpg) | Populated request-total and scrape-target panels |
| 19 | [Cloud inventory before update](screenshots/19-cloud-inventory-before-update.jpg) | Earlier version for comparison with screenshot 03 |
| 20 | [Equipment edit and search](screenshots/20-equipment-edit-and-search.jpg) | Updated quantity, low-stock status and location search |

The GitOps demonstration changed source `922bb1d` to `7ee0b7d`; screenshots 19
and 03 show the visible subtitle change. Later delivery runs retain the same
pipeline gates. Screenshots record the execution at their capture time.

[Execution records](records/README.md) contain logs, validation output, scan
reports and the persistence checks. [Troubleshooting notes](../evidence.md)
connect the observed failures to their diagnoses and fixes.

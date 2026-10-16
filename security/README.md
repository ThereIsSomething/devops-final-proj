# Security gates

The delivery workflow runs Ruff, Bandit SAST, pip-audit, npm audit, Trivy secret
scanning, and Trivy on both built images. Tests run before images are built.
HIGH or CRITICAL image vulnerabilities stop publication for that image and
stop GitOps promotion. No unfixed-CVE bypass is enabled.

Dependency checks query current advisory databases. A clean scan means no
matching known advisories at scan time; it does not guarantee the absence of
vulnerabilities. Preserve both scan artifacts and explain the actual result.

Database credentials are supplied through an existing Kubernetes Secret. They
must not be embedded in Helm values or committed to Git. The GitHub Actions
token publishes packages and writes the desired version; it holds no kubeconfig.
Flux reads the public Git repository and performs in-cluster deployment.

The classroom app has no end-user authentication. Its public demo is a shared,
editable sandbox: use synthetic equipment only. Grafana and Prometheus are
accessed through local port forwards, not public Ingress. For production, add
authentication/authorization, TLS, backups, network restrictions, and a managed
database according to the actual deployment requirements.

Runtime images use non-root users, Kubernetes drops Linux capabilities, and
application containers prohibit privilege escalation. PostgreSQL storage is
persistent but a single database pod is not a highly available database.

# Supporting execution records

These files support the [screenshots](../README.md) and
[troubleshooting runbook](../../../troubleshooting/README.md).

| Area | Records |
| --- | --- |
| Local application | [Compose build](docker-compose-build.txt), [runtime users/migration/HTTP checks](local-runtime-and-api-checks.txt), [API tests](api-tests.txt), [request logs](local-api-request-logs.txt), [saved browser edit in PostgreSQL](postgresql-browser-edit.txt) |
| Persistence | [Local restart/replacement result](local-persistence.txt), [before records](local-persistence-before.json), [after records](local-persistence-after.json), [cloud pod replacement](postgres-persistence.txt), [cloud records](postgres-persistence.json) |
| Infrastructure | [Azure validation](azure-validate.txt), [creation plan](azure-plan.txt), [apply](azure-apply.txt), [AWS validation](aws-validate.txt) |
| Delivery | [Application-update run](delivery-application-update.json), [security-scan run](delivery-security-scan-run.json), [cloud HTTP CRUD](cloud-smoke-after.txt) |
| Security | [Initial backend findings](security/initial-backend-findings.txt), [remediated backend](security/remediated-backend-scan.txt), [remediated frontend](security/remediated-frontend-scan.txt), [later backend scan](security/backend-image-scan.txt), [later frontend scan](security/frontend-image-scan.txt) |
| GitOps | [Source status](flux-source.txt), [release status](flux-release.txt), [before version](deployed-before.json), [after version](deployed-after.json) |
| Monitoring | [Metrics response](metrics.txt), [targets](prometheus-targets.json), [180-request load run](traffic.txt), [mobile layout measurement](mobile-layout.json) |
| Invalid image exercise | [Failure](broken-image-before.txt), [diagnosis](broken-image-diagnosis.txt), [recovered pod](broken-image-after.txt) |
| Service selector exercise | [Missing endpoints](broken-service-before.json), [pod labels](service-labels.txt), [corrected endpoints](broken-service-after.json), [HTTP success](service-http-status.txt) |
| Deployment issues | [Migration startup](migration-startup-failure.txt), [Grafana OOM](grafana-oom.txt), [Grafana recovery](grafana-recovered.txt) |

The records come from the documented execution runs. Some screenshots show later
checks; a supporting log is not necessarily the same command session pictured.

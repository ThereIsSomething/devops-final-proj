# Controlled troubleshooting exercises

Run these only in the separate `labshelf-troubleshooting` namespace. The files
are intentionally broken; they are not application deployment manifests. The
steps below reproduce the exercises. The [execution records](../docs/records)
contain the observed failures, diagnoses and recovery results.

## 1. Invalid image tag

```powershell
kubectl apply -f troubleshooting/namespace.yaml
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n labshelf-troubleshooting
kubectl describe pods -n labshelf-troubleshooting -l app=image-lab
kubectl get events -n labshelf-troubleshooting --sort-by=.lastTimestamp
kubectl set image deployment/image-lab web=nginxinc/nginx-unprivileged:stable-alpine -n labshelf-troubleshooting
kubectl rollout status deployment/image-lab -n labshelf-troubleshooting
```

Expected symptom: ErrImagePull/ImagePullBackOff. Investigate the event message,
registry path and tag. The deliberate tag does not exist. Recovery must be
confirmed by rollout status and an actual running pod; don't just change YAML.

Recorded results: [image pull failure](../docs/records/broken-image-before.txt),
[diagnostic output](../docs/records/broken-image-diagnosis.txt), and
[recovered pod](../docs/records/broken-image-after.txt).

## 2. Service without endpoints

Use the recovered image-lab Deployment from exercise 1:

```powershell
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get service service-lab -n labshelf-troubleshooting
kubectl get endpointslices -n labshelf-troubleshooting -l kubernetes.io/service-name=service-lab
kubectl get pods -n labshelf-troubleshooting --show-labels
kubectl set selector service/service-lab app=image-lab -n labshelf-troubleshooting
kubectl get endpointslices -n labshelf-troubleshooting -l kubernetes.io/service-name=service-lab
kubectl port-forward service/service-lab 8090:80 -n labshelf-troubleshooting
```

Open <http://localhost:8090> to verify traffic reaches Nginx. The root cause is
the mismatch between `app: incorrect-label` and the Deployment's `app: image-lab`.

Recorded results: [missing endpoints](../docs/records/broken-service-before.json),
[pod labels](../docs/records/service-labels.txt),
[corrected endpoints](../docs/records/broken-service-after.json), and
[HTTP success](../docs/records/service-http-status.txt).

## Deployment issues observed

| Issue | Diagnosis | Recovery |
| --- | --- | --- |
| Initial backend migration failure | PostgreSQL DNS/readiness timing before ready endpoints were available; [startup logs](../docs/records/migration-startup-failure.txt) | Kubernetes retried the init containers after PostgreSQL became ready; both backend replicas completed migrations |
| Grafana restart | The original 256 MiB limit caused [OOMKilled](../docs/records/grafana-oom.txt) | Increased the limit to 768 MiB and upgraded monitoring; [replacement status](../docs/records/grafana-recovered.txt) confirmed recovery |

The [security findings](../security/scan-findings.md) document the failed backend
image scan and the runtime change that passed the same security gate.

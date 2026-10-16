# Controlled troubleshooting exercises

Run these only in the separate `labshelf-troubleshooting` namespace. The files
are intentionally broken; they are not application deployment manifests. The
steps below reproduce the exercises. The [execution record](../docs/evidence.md)
contains the observed failures, diagnoses and recovery results.

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

For each exercise, explain the symptom, diagnostic output, root cause, fix and
recovery check. The saved examples are indexed in `docs/evidence.md`.

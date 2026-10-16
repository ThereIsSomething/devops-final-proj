# Delivery and Flux

GitHub Actions builds and scans both images, publishes commit-SHA tags to GHCR,
then commits the tested tag to `apps/labshelf-release.yaml`. Flux reads that
desired state and reconciles the Helm release. The promotion commit only changes
the GitOps path, so it does not recursively start another image build.

The workflow checks that its source commit is still the main branch head before
promoting. A newer commit prevents an older run from replacing the desired
version. Git push also rejects conflicting concurrent updates.

Install Flux controllers after AKS is ready:

```powershell
flux install --components=source-controller,kustomize-controller,helm-controller
kubectl apply -f gitops/source.yaml
flux get sources git -A
flux get helmreleases -A
```

Before bootstrap, create `labshelf` namespace and the existing `labshelf-db`
Secret, install monitoring CRDs, and ensure GHCR images can be pulled. The
`bootstrap` image tag is deliberately not a claim of a published release; the
first successful pipeline replaces it with an actual SHA before deployment.

No CI kubeconfig or Azure credential is needed. Cluster controllers read the
public source repository; private GHCR packages require an image pull Secret.
The application is reconciled by Flux; infrastructure and monitoring bootstrap
are documented manual/CLI operations, not falsely described as GitOps-managed.

For the demonstration, change visible app text, commit and push it, follow the
Actions run, then compare `/health` version and backend image tags before and
after Flux reconciliation. Preserve actual outputs and browser evidence.

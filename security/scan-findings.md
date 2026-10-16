# First image scan and response

The first delivery run, [38920205361](https://github.com/ThereIsSomething/devops-final-proj/actions/runs/38920205361),
passed the quality job and frontend image scan. The backend scan failed, so
GitOps promotion was skipped. The saved [Trivy report](../docs/records/security/initial-backend-findings.txt)
lists 44 HIGH/CRITICAL operating-system findings for Debian 13.7. These are
package findings, not necessarily 44 different CVEs. Its Python package checks
reported zero matching vulnerabilities.

One finding was **CVE-2026-76642** in util-linux packages. A failed external
mount helper can still trigger privileged post-mount hooks, potentially allowing
local privilege escalation. The installed Debian package was marked affected;
the [Debian tracker](https://security-tracker.debian.org/tracker/CVE-2026-76642)
and [upstream advisory](https://github.com/util-linux/util-linux/security/advisories/GHSA-m25x-3hj9-m26f)
explain the flaw. Package presence alone does not prove this application exposes
the necessary exploitation conditions.

The backend was changed to the official Alpine Python image, removing the
Debian runtime packages from the image. The HIGH/CRITICAL gate remains enabled
with no unfixed-vulnerability exemption. A replacement build must pass its own
scan before publication and deployment; changing the Dockerfile alone is not
proof of remediation.

The replacement run, [38920819802](https://github.com/ThereIsSomething/devops-final-proj/actions/runs/38920819802),
passed both image scans and the promotion job. The saved
[backend](../docs/records/security/remediated-backend-scan.txt) and
[frontend](../docs/records/security/remediated-frontend-scan.txt) reports record
the actual clean HIGH/CRITICAL results for commit `922bb1d`. This conclusion
applies to that build and scan time; later images still pass the same gate.

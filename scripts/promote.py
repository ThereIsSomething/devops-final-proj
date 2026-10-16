"""Update only the shared image tag after both image jobs pass."""

import re
import sys
from pathlib import Path

sha = sys.argv[1]
if not re.fullmatch(r"[0-9a-f]{40}", sha):
    raise SystemExit("Expected a complete Git commit SHA")
path = Path(__file__).resolve().parents[1] / "gitops/apps/labshelf-release.yaml"
text = path.read_text(encoding="utf-8")
updated, count = re.subn(r"(?m)^(    imageTag:) .*$", rf'\1 "{sha}"', text)
if count != 1:
    raise SystemExit("Expected exactly one imageTag in the HelmRelease")
path.write_text(updated, encoding="utf-8")

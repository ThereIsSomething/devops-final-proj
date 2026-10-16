"""Restart local Compose services and verify complete saved records survive.

Run from the repository root. Replaces the local PostgreSQL container while
preserving its named volume; does not touch the Azure deployment.
"""

import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--docker", default="docker")
args = parser.parse_args()
evidence = Path("docs/evidence")


def docker(*arguments):
    result = subprocess.run(
        [args.docker, *arguments], capture_output=True, text=True, check=True
    )
    print(result.stdout, end="", flush=True)
    print(result.stderr, end="", flush=True)
    return result.stdout.strip()


def records():
    with urllib.request.urlopen(
        "http://127.0.0.1:3000/api/equipment", timeout=3
    ) as response:
        return sorted(json.load(response), key=lambda record: record["id"])


def verify(stage):
    for attempt in range(1, 46):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/ready", timeout=3):
                pass
            after = records()
        except (OSError, TimeoutError):
            if attempt == 45:
                raise
            time.sleep(1)
            continue
        assert after == before, f"Saved records changed after {stage}"
        print(
            f"PASS {stage}: all {len(after)} complete records unchanged; attempt {attempt}",
            flush=True,
        )
        return after


before = records()
assert before, "Add sample equipment before checking persistence"
(evidence / "local-persistence-before.json").write_text(
    json.dumps(before, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(f"Baseline saved: {len(before)} equipment records", flush=True)
docker("compose", "restart", "backend")
verify("backend restart")
old_id = docker("compose", "ps", "-q", "postgres")
mount = "{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}"
old_mount = docker("inspect", old_id, "--format", mount)
docker(
    "compose",
    "up",
    "-d",
    "--force-recreate",
    "--no-deps",
    "--wait",
    "--wait-timeout",
    "120",
    "postgres",
)
new_id = docker("compose", "ps", "-q", "postgres")
assert new_id != old_id, "PostgreSQL container was not replaced"
assert docker("inspect", new_id, "--format", mount) == old_mount
after = verify("PostgreSQL container replacement using the same named volume")
(evidence / "local-persistence-after.json").write_text(
    json.dumps(after, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
docker(
    "compose",
    "exec",
    "-T",
    "postgres",
    "psql",
    "-U",
    "labshelf",
    "-d",
    "labshelf",
    "-c",
    "SELECT count(*) AS equipment_records, sum(quantity) AS total_units FROM equipment;",
)
docker("compose", "ps")

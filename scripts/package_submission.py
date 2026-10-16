"""Package tracked project files and validate the submission boundaries."""

import argparse
import hashlib
import json
import posixpath
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

EXCLUDED_DIRECTORIES = {
    ".git",
    ".local",
    ".terraform",
    ".venv",
    "__pycache__",
    "dist",
    "final-proj-detail",
    "handoff",
    "node_modules",
}
EXCLUDED_FILES = {
    "chat.md",
    "HANDOFF.md",
    "PROJECT_PLAN.md",
    "render-transcript.py",
}
REQUIRED_FILES = {
    "README.md",
    "SUBMISSION.md",
    "docker-compose.yml",
    ".github/workflows/delivery.yml",
    "backend/Dockerfile",
    "frontend/Dockerfile",
    "docs/requirements/grading-rubric.md",
    "docs/requirements/homework-requirements.md",
    "terraform/azure/terraform.tfvars.example",
    "terraform/aws/terraform.tfvars.example",
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
)


def excluded_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        return True
    if set(path.parts) & EXCLUDED_DIRECTORIES or path.name in EXCLUDED_FILES:
        return True
    if path.name.startswith(".env") and path.name != ".env.example":
        return True
    if path.name.startswith("kubeconfig") or ".tfstate" in path.name:
        return True
    if path.name.endswith(".tfvars") and not path.name.endswith(".tfvars.example"):
        return True
    return path.suffix in {".pem", ".key", ".tfplan", ".zip", ".bundle", ".db", ".pyc"}


def validate_links(files):
    failures = []
    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        for destination in re.findall(r"\]\(([^)]+)\)", data.decode("utf-8-sig")):
            destination = destination.strip().strip("<>")
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(name), unquote(parsed.path))
            )
            if target not in files and not any(
                candidate.startswith(target.rstrip("/") + "/") for candidate in files
            ):
                failures.append(f"{name}: missing archive link {destination}")
    if failures:
        raise SystemExit("\n".join(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("dist/submission/LabShelf-DevOps-Capstone.zip")
    )
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    names = sorted(name for name in tracked.decode("utf-8").split("\0") if name)
    forbidden = [name for name in names if excluded_path(name)]
    if forbidden:
        raise SystemExit("Private or generated files are tracked:\n" + "\n".join(forbidden))
    missing = REQUIRED_FILES - set(names)
    if missing:
        raise SystemExit("Required files missing:\n" + "\n".join(sorted(missing)))
    files = {}
    for name in names:
        source = root / name
        if source.is_symlink() or not source.is_file():
            raise SystemExit(f"Expected an ordinary file: {name}")
        data = source.read_bytes()
        text = data.decode("utf-8", errors="replace")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            raise SystemExit(f"Possible credential found in {name}; value withheld")
        files[name] = data
    validate_links(files)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "-c", "core.filemode=false", "status", "--porcelain", "--untracked-files=no"],
            cwd=root,
        ).strip()
    )
    manifest = {
        "source_revision": revision,
        "modified_tracked_files": dirty,
        "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    output = arguments.output
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr("LabShelf/" + name, data)
        archive.writestr("LabShelf/SUBMISSION_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise SystemExit("Archive integrity check failed")
        for name, digest in manifest["sha256"].items():
            if hashlib.sha256(archive.read("LabShelf/" + name)).hexdigest() != digest:
                raise SystemExit(f"Archive digest mismatch: {name}")
    temporary.replace(output)
    screenshots = sum(name.startswith("docs/evidence/screenshots/") for name in files)
    print(f"Created {output}")
    print(f"Verified {len(files)} files, {screenshots} screenshots, links, and SHA-256 digests.")
    print(f"Source revision: {revision}; modified tracked files: {dirty}")
    print("Credential checks cover common key/token formats, not every possible secret.")


if __name__ == "__main__":
    main()

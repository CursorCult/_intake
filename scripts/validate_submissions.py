#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def changed_submission_files_from_ci() -> list[Path]:
    base_sha = (os.getenv("BASE_SHA") or "").strip()
    head_sha = (os.getenv("HEAD_SHA") or "").strip()
    if not base_sha or not head_sha:
        return []

    raw = subprocess.check_output(["git", "diff", "--name-only", base_sha, head_sha], text=True)
    paths = [Path(p.strip()) for p in raw.splitlines() if p.strip()]
    return [p for p in paths if p.parts and p.parts[0] == "submissions" and p.suffix in {".yml", ".yaml"}]


def parse_yaml_minimal(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except Exception:
        raise SystemExit("PyYAML not available. Install it (e.g. `pip install PyYAML`).")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML must be a mapping at the root.")
    return data


def validate_schema(doc: dict, path: Path) -> list[str]:
    errors: list[str] = []
    project = doc.get("project")
    if not isinstance(project, dict):
        return ["Missing required mapping: project"]

    required = ["repo", "source", "owner", "license", "description"]
    for key in required:
        value = project.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"project.{key} must be a non-empty string")

    repo = project.get("repo")
    if isinstance(repo, str) and repo.strip():
        if "/" in repo or repo.strip() != repo:
            errors.append("project.repo must be a bare repo name (no org/user, no spaces)")

    return errors


def main() -> int:
    argv_paths = [Path(p) for p in sys.argv[1:]]
    if argv_paths:
        files = argv_paths
    else:
        files = changed_submission_files_from_ci()
        if not files:
            files = sorted(
                [
                    p
                    for p in Path("submissions").glob("*.y*ml")
                    if p.name != "_template.yml"
                ]
            )

    if not files:
        print("No submission files found; nothing to validate.")
        return 0

    if len(argv_paths) == 0 and os.getenv("GITHUB_ACTIONS") == "true" and len(files) != 1:
        print("Expected exactly 1 submission file change; got:", [str(f) for f in files])
        return 1

    for path in files:
        doc = parse_yaml_minimal(path)
        errors = validate_schema(doc, path)
        if errors:
            print(f"Invalid submission {path}:")
            for e in errors:
                print("-", e)
            return 1
        print("OK:", path)
        print(json.dumps(doc, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import yaml
import urllib.request
import re # Added for regex
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple # Added for type hints


# --- GitHub API Helpers (Copied/Adapted from .github/scripts/update_rules_lists.py) ---
def _github_token_optional() -> str | None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    return token.strip() if token else None

class GitHubApiError(Exception): # Changed from RuntimeError to Exception to allow custom init
    def __init__(self, status: int, url: str, body: str):
        super().__init__(f"GitHub API error {status} for {url}: {body}")
        self.status = status
        self.url = url
        self.body = body

def _request_json(url: str, token: str | None) -> tuple[Any, Dict[str, str]]:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "CursorCult-Intake-Processor")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return json.loads(raw), headers
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise GitHubApiError(status=e.code, url=url, body=body) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e}") from e
# ----------------------------------------------------------------------------------


def check_license(url):
    print(f"Checking license for {url}...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "clone", "--depth", "1", url, tmp], 
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            lic = Path(tmp) / "LICENSE"
            if lic.exists():
                text = lic.read_text("utf-8").lower()
                if "unlicense" in text or "public domain" in text:
                    return "Unlicense"
                return "Other"
    except Exception as e:
        print(f"  Error cloning for license check: {e}")
    return "Unknown"

def get_repo_archived_status(source_url: str, token: str | None) -> bool:
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)", source_url)
    if not m:
        return False
    owner, repo_name = m.groups()
    repo_name = repo_name.replace(".git", "")
    
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    try:
        data, _ = _request_json(api_url, token)
        return data.get("archived", False)
    except GitHubApiError as e:
        if e.status == 404:
            return False # Repo not found, so not archived by definition
        print(f"  Warning: Failed to fetch archived status for {owner}/{repo_name}: {e}")
        return False
    except Exception as e:
        print(f"  Warning: Unexpected error fetching archived status for {owner}/{repo_name}: {e}")
        return False


def main() -> int:
    registry_file = Path("registry.json")
    if registry_file.exists():
        registry = json.loads(registry_file.read_text("utf-8"))
    else:
        registry = {}

    submissions_dir = Path("submissions")
    if not submissions_dir.exists():
        return 0 # No submissions to process

    github_token = _github_token_optional()

    for yaml_file in submissions_dir.glob("*.yml"):
        if yaml_file.name == "_template.yml": continue
        
        try:
            data = yaml.safe_load(yaml_file.read_text("utf-8"))
            
            # Handle both old nested and new flat formats
            name, url, desc, maint = None, None, None, None
            if "project" in data: # Legacy format
                p = data["project"]
                name = p.get("repo")
                url = p.get("source")
                desc = p.get("description")
                maint = p.get("owner")
            else: # New flat format
                name = data.get("name")
                url = data.get("source_url")
                desc = data.get("description")
                maint = data.get("maintainer")

            if not name or not url:
                print(f"Skipping {yaml_file}: missing name or source_url", file=sys.stderr)
                continue

            # Check if license and archived status need to be re-fetched
            entry = registry.get(name)
            current_url = entry.get("source_url") if entry else None
            
            license_type = entry.get("license", "Unknown") if entry else "Unknown"
            if current_url != url or license_type == "Unknown": # Refetch if URL changed or unknown
                license_type = check_license(url)
            
            archived_status = entry.get("archived", False) if entry else False
            if current_url != url or "archived" not in entry: # Refetch if URL changed or not present
                archived_status = get_repo_archived_status(url, github_token)

            registry[name] = {
                "name": name,
                "description": desc,
                "source_url": url,
                "maintainer": maint,
                "license": license_type,
                "archived": archived_status
            }
        except Exception as e:
            print(f"Failed to process {yaml_file}: {e}", file=sys.stderr)

    registry_file.write_text(json.dumps(registry, indent=2, sort_keys=True), "utf-8")
    print("Registry updated.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
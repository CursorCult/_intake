#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path

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
        print(f"  Error cloning: {e}")
    return "Unknown"

def main():
    registry_file = Path("registry.json")
    if registry_file.exists():
        registry = json.loads(registry_file.read_text("utf-8"))
    else:
        registry = {}

    submissions_dir = Path("submissions")
    if not submissions_dir.exists():
        return

    for yaml_file in submissions_dir.glob("*.yml"):
        if yaml_file.name == "_template.yml": continue
        
        try:
            data = yaml.safe_load(yaml_file.read_text("utf-8"))
            # Handle both formats
            if "project" in data:
                p = data["project"]
                name = p.get("repo")
                url = p.get("source")
                desc = p.get("description")
                maint = p.get("owner")
            else:
                name = data.get("name")
                url = data.get("source_url")
                desc = data.get("description")
                maint = data.get("maintainer")

            if not name or not url: continue

            entry = registry.get(name)
            if entry and entry.get("source_url") == url:
                # Assume license is stable to avoid cloning on every run
                license_type = entry.get("license", "Unknown")
            else:
                license_type = check_license(url)

            registry[name] = {
                "name": name,
                "description": desc,
                "source_url": url,
                "maintainer": maint,
                "license": license_type
            }
        except Exception as e:
            print(f"Failed to process {yaml_file}: {e}")

    registry_file.write_text(json.dumps(registry, indent=2, sort_keys=True), "utf-8")
    print("Registry updated.")

if __name__ == "__main__":
    main()

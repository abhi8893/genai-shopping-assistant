#!/usr/bin/env python3
"""Check if a venv exists for a component (either physical or active)."""

import argparse
import json
import sys
from pathlib import Path


def venv_exists(repo_root: Path, component: str, group: str) -> bool:
    """Check if a venv exists (physical .venv-{group} or active .venv).

    Args:
        repo_root: Repository root directory
        component: Component path relative to repo root
        group: Venv group (e.g., 'dev', 'prod')

    Returns:
        True if venv exists, False otherwise
    """
    if component == "root":
        component_path = repo_root
    else:
        component_path = repo_root / component

    venv_name = f".venv-{group}"

    # Check if physical .venv-{group} exists
    physical_venv = component_path / venv_name
    if physical_venv.exists():
        return True

    # Check if .venv exists and is active with the requested group
    active_venv = component_path / ".venv"
    if active_venv.exists():
        info_file = component_path / ".info.json"
        if info_file.exists():
            try:
                with open(info_file) as f:
                    data = json.load(f)
                # If active is set to this venv name, it exists (just renamed)
                if data.get("venv", {}).get("active") == venv_name:
                    return True
            except Exception:
                pass

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Check if a venv exists for a component (physical or active)"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )
    parser.add_argument("--group", required=True, help="Venv group (e.g., dev, prod)")

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    exists = venv_exists(repo_root, args.component, args.group)

    # Exit with 0 if exists, 1 if not (standard Unix convention)
    sys.exit(0 if exists else 1)


if __name__ == "__main__":
    main()

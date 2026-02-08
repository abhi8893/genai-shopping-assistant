#!/usr/bin/env python3
"""Script to clean virtual environments for monorepo components."""

import argparse
import shutil
import sys
from pathlib import Path


def clean_venvs(repo_root: Path, component: str) -> int:
    """Remove all .venv-* directories from the specified component."""
    component_path = repo_root / component

    if not component_path.exists():
        print(
            f"Error: Component path does not exist: {component_path}", file=sys.stderr
        )
        return 1

    print(f"Cleaning virtual environments in {component}...")

    # Find and remove all .venv-* directories
    venv_dirs = list(component_path.glob(".venv-*"))

    if not venv_dirs:
        print("No virtual environments found to clean")
        return 0

    for venv_dir in venv_dirs:
        if venv_dir.is_dir():
            print(f"Removing {venv_dir.name}...")
            shutil.rmtree(venv_dir)

    print(f"✓ Cleaned {len(venv_dirs)} virtual environment(s)")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Clean virtual environments for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    sys.exit(clean_venvs(repo_root, args.component))


if __name__ == "__main__":
    main()

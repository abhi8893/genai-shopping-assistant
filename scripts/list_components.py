#!/usr/bin/env python3
"""Script to discover all components in the monorepo that have pyproject.toml."""

import argparse
import sys
from pathlib import Path


def list_components(repo_root: Path) -> list[str]:
    """Find all components with pyproject.toml files."""
    components = ["root"]

    # Search in packages/ and services/ directories
    search_dirs = ["packages", "services"]

    for search_dir in search_dirs:
        search_path = repo_root / search_dir
        if not search_path.exists():
            continue

        # Find all pyproject.toml files, excluding venvs
        for pyproject_file in search_path.rglob("pyproject.toml"):
            # Skip if inside a virtual environment
            if any(part.startswith(".venv") for part in pyproject_file.parts):
                continue

            # Get the component path relative to repo root
            component_path = pyproject_file.parent.relative_to(repo_root)
            components.append(str(component_path))

    return [components[0]] + sorted(components[1:])


def main():
    parser = argparse.ArgumentParser(
        description="List all components in the monorepo with pyproject.toml"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    components = list_components(repo_root)

    # Print one per line for easy parsing in shell scripts
    for component in components:
        print(component)

    return 0


if __name__ == "__main__":
    sys.exit(main())

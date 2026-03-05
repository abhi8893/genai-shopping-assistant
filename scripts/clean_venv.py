#!/usr/bin/env python3
"""Script to clean virtual environments for monorepo components."""

import argparse
import glob
import json
import os
import shutil
import sys
from pathlib import Path


# TODO: lol Claude led to a high cyclomatic complexity, need to refactor
def clean_venvs(  # noqa: C901, PLR0912, PLR0915
    repo_root: Path, component: str, group: str | None = None, clear_info: bool = False
) -> int:
    """Remove .venv-* directories from the specified component.

    Args:
        repo_root: Repository root directory
        component: Component path relative to repo root
        group: Specific venv group to clean (dev, prod, test, etc.).
            If None, cleans all venvs.
        clear_info: Whether to clear the .info.json file after cleaning
    """
    if component == "root":
        component_path = repo_root
    else:
        component_path = repo_root / component

    if not component_path.exists():
        print(
            f"Error: Component path does not exist: {component_path}", file=sys.stderr
        )
        return 1

    # Load .info.json to check active venv
    info_file = component_path / ".info.json"
    current_active = None
    if info_file.exists():
        try:
            with open(info_file) as f:
                data = json.load(f)
            current_active = data.get("venv", {}).get("active")
        except Exception:
            pass

    # Determine which venvs to clean
    venv_name = None
    if group:
        if group == "dev":
            venv_name = ".venv-dev"
        elif group == "prod":
            venv_name = ".venv-prod"
        else:
            venv_name = f".venv-{group}"

        print(f"Cleaning {venv_name} in {component}...")

        # If this group is currently active, it's at .venv, not .venv-{group}
        if current_active == venv_name:
            venv_path = component_path / ".venv"
            print(f"  Note: {venv_name} is currently active (at .venv)")
        else:
            venv_path = component_path / venv_name

        if venv_path.exists() and venv_path.is_dir():
            print(f"Removing {venv_name}...")
            shutil.rmtree(venv_path)
            print(f"✓ Cleaned {venv_name}")
        else:
            print(f"No {venv_name} found to clean")
    else:
        print(f"Cleaning all virtual environments in {component}...")

        # Find and remove all .venv-* directories
        venv_dirs = list(component_path.glob(".venv*"))

        if not venv_dirs:
            print("No virtual environments found to clean")
        else:
            for venv_dir in venv_dirs:
                if venv_dir.is_dir():
                    print(f"Removing {venv_dir.name}...")
                    shutil.rmtree(venv_dir)

            print(f"✓ Cleaned {len(venv_dirs)} virtual environment(s)")

    # Update .info.json to reflect current state
    if info_file.exists():
        if clear_info:
            # Clear all venv info
            data = {"venv": {"options": [], "active": None}}
        else:
            # Update to reflect remaining venvs
            venv_available = [
                os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
            ]
            with open(info_file) as f:
                data = json.load(f)
            data["venv"]["options"] = sorted(venv_available)

            # If we just deleted the active venv, clear the active field
            if group and current_active == venv_name:
                data["venv"]["active"] = None

        with open(info_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✓ Updated {info_file}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Clean virtual environments for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )
    parser.add_argument(
        "--group",
        help="Specific venv group to clean (dev, prod, test, etc.). "
        "If not specified, cleans all venvs.",
    )
    parser.add_argument(
        "--clear-info",
        action="store_true",
        help="Clear all venv info in .info.json (use with caution)",
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    sys.exit(clean_venvs(repo_root, args.component, args.group, args.clear_info))


if __name__ == "__main__":
    main()

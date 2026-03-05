#!/usr/bin/env python3
"""Script to unswitch (deactivate) virtual environments in monorepo components."""

import argparse
import glob
import json
import os
import sys
from pathlib import Path


def unswitch_venv(repo_root: Path, component: str) -> int:
    """Unswitch (deactivate) a virtual environment.

    Reverses venv-switch by renaming .venv back to .venv-{active}.

    Args:
        repo_root: Repository root directory
        component: Component path relative to repo root

    Returns:
        0 if successful, 1 if there are errors
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

    info_file = component_path / ".info.json"
    default_venv = component_path / ".venv"

    # Load .info.json
    if not info_file.exists():
        print(
            f"Error: .info.json not found in {component}. "
            "Run 'make venv-refresh' first.",
            file=sys.stderr,
        )
        return 1

    with open(info_file) as f:
        data = json.load(f)

    current_active = data["venv"].get("active")

    # Check if there's an active venv
    if not current_active:
        print(f"ℹ No active venv in {component}, nothing to unswitch")
        return 0

    # Check if .venv exists
    if not default_venv.exists():
        print(
            f"Error: .venv directory not found in {component}. "
            f"Expected to find active venv {current_active}",
            file=sys.stderr,
        )
        return 1

    print(f"Unswitching from {current_active} in {component}...")

    # Rename .venv back to .venv-{active}
    target_venv_path = component_path / current_active

    print(f"  Renaming .venv → {current_active}...")
    try:
        default_venv.rename(target_venv_path)
        print(f"  ✓ Renamed .venv → {current_active}")
    except Exception as e:
        print(f"Error renaming .venv: {e}", file=sys.stderr)
        return 1

    # Update .info.json to clear active
    venv_available = [
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    ]
    data["venv"]["options"] = sorted(venv_available)
    data["venv"]["active"] = None

    with open(info_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✓ Unswitched from {current_active}")
    print(f"✓ To activate: source {target_venv_path}/bin/activate")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Unswitch (deactivate) a virtual environment for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    sys.exit(unswitch_venv(repo_root, args.component))


if __name__ == "__main__":
    main()

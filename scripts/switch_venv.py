#!/usr/bin/env python3
"""Script to switch between virtual environments in monorepo components."""

import argparse
import glob
import json
import os
import sys
from pathlib import Path


def switch_venv(repo_root: Path, component: str, target_venv: str) -> int:  # noqa: C901
    """Switch to a different virtual environment.

    Args:
        repo_root: Repository root directory
        component: Component path relative to repo root
        target_venv: Name of the venv to switch to (e.g., '.venv-dev' or 'dev')

    Returns:
        0 if successful, 1 if there are errors
    """
    component_path = repo_root / component

    if not component_path.exists():
        print(
            f"Error: Component path does not exist: {component_path}", file=sys.stderr
        )
        return 1

    # Normalize target_venv name
    if not target_venv.startswith(".venv-"):
        target_venv = f".venv-{target_venv}"

    info_file = component_path / ".info.json"
    default_venv = component_path / ".venv"
    target_venv_path = component_path / target_venv

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

    # Check if already active — must come before the existence check because when a
    # venv is active its directory has been renamed to .venv, so target_venv_path
    # won't exist as a physical directory.
    if current_active == target_venv:
        if default_venv.exists():
            print(f"✓ {target_venv} is already the active venv, nothing to do")
            return 0
        print(f"⚠ {target_venv} is marked as active in .info.json but .venv is missing")
        print("  Proceeding with switch to repair state...")

    # Check if target venv exists
    if not target_venv_path.exists():
        print(
            f"Error: Target venv '{target_venv}' does not exist in {component}",
            file=sys.stderr,
        )

        # List available venvs
        available_venvs = [
            os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
        ]
        if available_venvs:
            print(f"Available venvs: {available_venvs}")
        else:
            print("No venvs found. Create one with 'make venv-create'")

        if default_venv.exists() and current_active:
            print(
                f"Note: .venv exists (currently active: {current_active}). "
                "It can be switched to another venv."
            )

        return 1

    print(f"Switching to {target_venv} in {component}...")

    # Step 1: If something is currently active, rename .venv back to original name
    if current_active and default_venv.exists():
        print(f"  Deactivating {current_active}...")
        old_venv_path = component_path / current_active
        default_venv.rename(old_venv_path)
        print(f"  Renamed .venv → {current_active}")

    # Step 2: Check if target venv exists now (it should)
    if not target_venv_path.exists():
        print(
            f"Error: {target_venv} not found after deactivation. Something went wrong.",
            file=sys.stderr,
        )
        return 1

    # Step 3: Rename target venv to .venv
    print(f"  Activating {target_venv}...")
    target_venv_path.rename(default_venv)
    print(f"  Renamed {target_venv} → .venv")

    # Step 4: Update .info.json
    # Options should be union of physically present .venv-* and active venv
    venv_available = [
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    ]
    all_venvs = set(venv_available)
    all_venvs.add(target_venv)  # Add the active one
    data["venv"]["options"] = sorted(all_venvs)
    data["venv"]["active"] = target_venv

    with open(info_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✓ Switched to {target_venv}")
    print("✓ To activate: source .venv/bin/activate")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Switch between virtual environments for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target venv to switch to (e.g., 'dev', 'prod', or '.venv-dev')",
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    sys.exit(switch_venv(repo_root, args.component, args.target))


if __name__ == "__main__":
    main()

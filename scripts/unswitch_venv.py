#!/usr/bin/env python3
"""Script to unswitch (deactivate) virtual environments in monorepo components."""

import argparse
import glob
import json
import os
import shutil
import sys
from pathlib import Path

from list_components import list_components
from repair_venv_references import repair_venv_references  # noqa: E402


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
        # Handle edge case: if target already exists (corrupt state), remove it first
        if target_venv_path.exists():
            print(f"  Warning: {current_active} already exists, removing it first")
            shutil.rmtree(target_venv_path)

        default_venv.rename(target_venv_path)
        print(f"  ✓ Renamed .venv → {current_active}")
        repair_venv_references(target_venv_path)
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


def _check_unswitch_result(repo_root: Path, component: str) -> tuple[bool, bool]:  # noqa: C901
    """Check if component was unswitched or had no active venv.

    Returns:
        (was_unswitched, had_no_active)
    """
    if component == "root":
        component_path = repo_root
    else:
        component_path = repo_root / component

    info_file = component_path / ".info.json"
    if not info_file.exists():
        return False, False

    with open(info_file) as f:
        data = json.load(f)

    # If active is None, it had no active venv (informational case)
    if data["venv"].get("active") is None:
        # Check if there were any venvs at all
        if not data["venv"].get("options"):
            return False, True
        return True, False

    return True, False


def unswitch_all_venvs(repo_root: Path) -> int:  # noqa: C901, PLR0912
    """Unswitch all virtual environments in all components.

    Gracefully handles components with no active venv (treats as informational).

    Args:
        repo_root: Repository root directory

    Returns:
        0 if completed (even with some components having no active venv)
        1 if there are actual errors
    """
    components = list_components(repo_root)

    succeeded = 0
    had_no_active = 0
    failed_list = []

    print("Unswitching virtual environments for all components...")

    for component in components:
        print(f"\n==> Unswitching venv for {component}...")

        # Try to unswitch
        result = unswitch_venv(repo_root, component)

        if result == 0:
            was_unswitched, had_no_active_venv = _check_unswitch_result(
                repo_root, component
            )
            if was_unswitched:
                succeeded += 1
                print("    ✓ Successfully unswitched")
            elif had_no_active_venv:
                had_no_active += 1
                print("    ℹ No active venv to unswitch")
        else:
            # Actual error occurred
            failed_list.append(component)

    # Print summary
    print()
    print("=" * 40)
    summary = f"Unswitch Summary: {succeeded} unswitched"
    summary += f", {had_no_active} had no active venv"
    print(summary)
    print("=" * 40)

    if succeeded == 0 and had_no_active > 0:
        print()
        print("ℹ No active venvs to unswitch in all components.")
        print("Components are already in independent state.")
        print()
    elif had_no_active > 0:
        print()
        print("ℹ Some components had no active venv (already independent).")
        print()

    if failed_list:
        print()
        print("✗ Errors occurred in the following components:")
        for component in failed_list:
            print(f"  - {component}")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Unswitch (deactivate) a virtual environment for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component",
        help="Component path relative to repo root (required if not --all)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Unswitch all components in the monorepo"
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)

    if args.all:
        sys.exit(unswitch_all_venvs(repo_root))
    elif args.component:
        sys.exit(unswitch_venv(repo_root, args.component))
    else:
        parser.error("Either --component or --all must be specified")


if __name__ == "__main__":
    main()

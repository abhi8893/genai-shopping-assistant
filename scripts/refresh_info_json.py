#!/usr/bin/env python3
"""Script to refresh .info.json files for monorepo components."""

import argparse
import glob
import json
import os
import sys
from pathlib import Path


def refresh_info_json(repo_root: Path, component: str, fix_active: bool = False) -> int:  # noqa: PLR0915, PLR0912, C901
    """Refresh .info.json for a component and validate the active field.

    Args:
        repo_root: Repository root directory
        component: Component path relative to repo root
        fix_active: If True, automatically set active to None if invalid

    Returns:
        0 if successful, 1 if there are validation errors
    """
    component_path = repo_root / component

    if not component_path.exists():
        print(
            f"Error: Component path does not exist: {component_path}", file=sys.stderr
        )
        return 1

    info_file = component_path / ".info.json"

    # Step 1: Read .venv-* available in the component's dir
    venv_available = [
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    ]

    # Load or create .info.json
    if info_file.exists():
        with open(info_file) as f:
            data = json.load(f)
    else:
        data = {"venv": {"options": [], "active": None}}

    # Update options: union of physically present .venv-* and active venv
    current_active = data["venv"].get("active")
    all_venvs = set(venv_available)
    if current_active and current_active.startswith(".venv-"):
        all_venvs.add(current_active)

    data["venv"]["options"] = sorted(all_venvs)

    # Step 2: Check if .venv is present and validate active field
    default_venv_exists = (component_path / ".venv").exists()
    active = data["venv"].get("active")
    is_valid = True
    validation_errors = []

    if active is not None:
        # Validation: active should not be ".venv"
        if active == ".venv":
            is_valid = False
            validation_errors.append(
                '  - active field is set to ".venv" (not a managed venv name)'
            )

        # Validation: if active is set to .venv-{id}, then .venv-{id} must NOT exist
        # (it should have been renamed to .venv when activated)
        if active.startswith(".venv-"):
            if active in venv_available:
                is_valid = False
                validation_errors.append(
                    f"  - active field is '{active}' but '{active}' directory "
                    "still exists (should have been renamed to .venv when activated)"
                )

            # Check if .venv exists when something is active
            if not default_venv_exists:
                is_valid = False
                validation_errors.append(
                    f"  - active field is '{active}' but .venv directory "
                    "does not exist (active venv should exist as .venv)"
                )
        # Invalid format
        elif not active.startswith(".venv-"):
            is_valid = False
            validation_errors.append(
                f"  - active field '{active}' is not a valid venv name "
                "(should be .venv-{id} format)"
            )

    # Step 3: Handle invalid active field
    if not is_valid:
        if fix_active:
            data["venv"]["active"] = None
            with open(info_file, "w") as f:
                json.dump(data, f, indent=4)
            print(f"⚠ Fixed invalid active field in {component}")
            print("  Validation errors:")
            for error in validation_errors:
                print(error)
            print("  → Set active to null")
            print(f"✓ Updated {info_file}")
            return 0
        # Save the updated options but keep the invalid active field
        with open(info_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"⚠ Validation errors in {component}:")
        for error in validation_errors:
            print(error)
        print(f"\nAvailable venvs: {data['venv']['options']}")
        print(f"Current active: {active if active else 'null'}")
        print(f"\nPlease fix the active field in {info_file} or run with --fix-active")
        return 1
    # Step 4: Valid - just update the file
    with open(info_file, "w") as f:
        json.dump(data, f, indent=4)

    # Provide info about .venv if it exists
    if default_venv_exists:
        print(
            f"ℹ Note: Default .venv directory exists in {component} "
            "(not managed by this tool)"
        )

    print(f"✓ Refreshed {info_file}")
    if data["venv"]["options"]:
        print(f"  Available venvs: {data['venv']['options']}")
        print(f"  Active: {active if active else 'null'}")
    else:
        print("  No managed venvs found")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Refresh .info.json for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )
    parser.add_argument(
        "--fix-active",
        action="store_true",
        help="Automatically set active to null if invalid",
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    sys.exit(refresh_info_json(repo_root, args.component, args.fix_active))


if __name__ == "__main__":
    main()

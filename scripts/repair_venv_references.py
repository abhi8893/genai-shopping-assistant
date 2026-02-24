#!/usr/bin/env python3
"""Utility to repair stale VIRTUAL_ENV path references in venv activate scripts.

After a venv directory is renamed (e.g. .venv-dev → .venv), the activate scripts
inside bin/ still contain hardcoded paths to the old name. This script scans all
regular files in bin/ and replaces any stale references with the correct current path.
"""

import argparse
import re
import sys
from pathlib import Path


def repair_venv_references(venv_dir: Path, dry_run: bool = False) -> int:
    """Repair stale VIRTUAL_ENV path references in venv activate scripts.

    Args:
        venv_dir: Path to the venv directory (e.g. .venv or .venv-dev)
        dry_run: If True, report changes without writing them

    Returns:
        0 on success, 1 on error
    """
    venv_dir = venv_dir.resolve()

    if not venv_dir.exists():
        print(f"Error: venv directory does not exist: {venv_dir}", file=sys.stderr)
        return 1

    bin_dir = venv_dir / "bin"
    if not bin_dir.exists():
        print(f"Error: bin/ directory not found in {venv_dir}", file=sys.stderr)
        return 1

    parent = re.escape(str(venv_dir.parent))
    pattern = re.compile(rf"{parent}/\.venv(?:-[a-zA-Z0-9_-]*)?")
    replacement = str(venv_dir)

    updated = 0
    for file_path in bin_dir.iterdir():
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        new_content = pattern.sub(replacement, content)
        if new_content == content:
            continue

        prefix = "[dry-run] " if dry_run else ""
        print(f"{prefix}Updated {file_path.name}: stale path → '{replacement}'")

        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")

        updated += 1

    if updated == 0:
        print(f"No stale references found in {bin_dir}")
    else:
        action = "Would update" if dry_run else "Updated"
        print(f"{action} {updated} file(s) in {bin_dir}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Repair stale VIRTUAL_ENV path references in venv activate scripts"
    )
    parser.add_argument(
        "--venv-dir",
        required=True,
        help="Path to the component directory (e.g. packages/shopping-assistant)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Venv suffix to check (e.g. 'dev' checks .venv-dev). Omit to check .venv",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing them",
    )

    args = parser.parse_args()
    component_dir = Path(args.venv_dir)
    venv_dir = component_dir / (f".venv-{args.target}" if args.target else ".venv")
    sys.exit(repair_venv_references(venv_dir, dry_run=args.dry_run))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Script to build uv lockfiles for monorepo components by running `uv lock`."""

import argparse
import subprocess
import sys
from pathlib import Path

# Allow importing list_components from sibling script
sys.path.insert(0, str(Path(__file__).parent))
from list_components import list_components  # noqa: E402


def build_lockfile(component_path: Path) -> int:
    """Run `uv lock` in the component directory."""

    print(f"Building lockfile for {component_path}...")
    try:
        subprocess.run(["uv", "lock"], cwd=component_path, check=True)
        print(f"✓ Lockfile built for {component_path}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error building lockfile for {component_path}: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build uv lockfiles for monorepo components"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--component", help="Component path relative to repo root"
    )
    target_group.add_argument(
        "--all-components",
        action="store_true",
        help="Build lockfiles for all components",
    )

    args = parser.parse_args()
    repo_root = Path(args.repo_root)

    if args.all_components:
        components = list_components(repo_root)
        if not components:
            print("No components found.", file=sys.stderr)
            return 1

        failed = 0
        for component in components:
            print()
            print(f"==> {component}")
            if component == "root":
                component_path = repo_root
            else:
                component_path = repo_root / component

            result = build_lockfile(component_path)
            if result != 0:
                failed += 1

        print()
        if failed:
            print(f"⚠ {failed} component(s) failed to build lockfile", file=sys.stderr)
            return 1

        print("✓ All lockfiles built successfully")
        return 0

    if args.component == "root":
        component_path = repo_root
    else:
        component_path = repo_root / args.component

    if not component_path.exists():
        print(
            f"Error: Component path does not exist: {component_path}",
            file=sys.stderr,
        )
        return 1
    return build_lockfile(component_path)


if __name__ == "__main__":
    sys.exit(main())

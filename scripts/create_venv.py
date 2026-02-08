#!/usr/bin/env python3
"""Script to create and manage virtual environments for monorepo components."""

import argparse
import glob
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


def update_info_json(component_path: Path) -> None:
    """Update .info.json with the new venv information."""
    info_file = component_path / ".info.json"

    if info_file.exists():
        with open(info_file) as f:
            data = json.load(f)
    else:
        data = {"venv": {"options": [], "active": None}}

    venv_available = [
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    ]

    data["venv"]["options"] = sorted(venv_available)

    with open(info_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Updated {info_file}")


def get_path_dependencies(component_path: Path) -> list[tuple[str, Path]]:
    """Get path-based dependencies from [tool.uv.sources] in pyproject.toml."""
    pyproject_path = component_path / "pyproject.toml"

    if not pyproject_path.exists():
        return []

    try:
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)

        uv_sources = config.get("tool", {}).get("uv", {}).get("sources", {})
        path_deps = []

        for dep_name, dep_config in uv_sources.items():
            if isinstance(dep_config, dict) and "path" in dep_config:
                dep_path = component_path / dep_config["path"]
                path_deps.append((dep_name, dep_path))

        return path_deps
    except Exception as e:
        print(f"Warning: Could not parse pyproject.toml: {e}", file=sys.stderr)
        return []


def create_venv(repo_root: Path, component: str, group: str) -> int:
    """Create a virtual environment for the specified component and group."""
    component_path = repo_root / component

    if not component_path.exists():
        print(
            f"Error: Component path does not exist: {component_path}", file=sys.stderr
        )
        return 1

    # Determine venv name based on group
    if group == "dev":
        venv_name = ".venv-dev"
    elif group == "prod":
        venv_name = ".venv-prod"
    else:
        venv_name = f".venv-{group}"

    venv_path = component_path / venv_name

    print(f"Creating virtual environment for {component}...")

    # Create venv using uv
    try:
        subprocess.run(
            ["uv", "venv", venv_name, "--python", "3.12"],
            cwd=component_path,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error creating venv: {e}", file=sys.stderr)
        return 1

    # Install dependencies based on group
    print(f"Installing {component} dependencies...")
    try:
        if group == "dev":
            print("Installing with dev dependencies (editable)...")
            subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    venv_name,
                    "-e",
                    ".",
                    "--group",
                    "dev",
                ],
                cwd=component_path,
                check=True,
            )

            # For dev mode, reinstall path-based dependencies in editable mode
            path_deps = get_path_dependencies(component_path)
            if path_deps:
                print("Reinstalling internal dependencies in editable mode...")
                for dep_name, dep_path in path_deps:
                    print(f"  Installing {dep_name} from {dep_path} (editable)...")
                    subprocess.run(
                        [
                            "uv",
                            "pip",
                            "install",
                            "--python",
                            venv_name,
                            "-e",
                            str(dep_path),
                        ],
                        cwd=component_path,
                        check=True,
                    )

        elif group == "prod":
            print("Installing for production (non-editable)...")
            subprocess.run(
                ["uv", "pip", "install", "--python", venv_name, "."],
                cwd=component_path,
                check=True,
            )
        else:
            print(f"Installing with {group} group (non-editable)...")
            subprocess.run(
                ["uv", "pip", "install", "--python", venv_name, ".", "--group", group],
                cwd=component_path,
                check=True,
            )
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}", file=sys.stderr)
        return 1

    # Update .info.json
    update_info_json(component_path)

    print(f"✓ Virtual environment created at {venv_path}")
    print(f"✓ To activate: source {venv_path}/bin/activate")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Create virtual environment for monorepo component"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component", required=True, help="Component path relative to repo root"
    )
    parser.add_argument(
        "--group", default="prod", help="Dependency group (dev, prod, test, etc.)"
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    sys.exit(create_venv(repo_root, args.component, args.group))


if __name__ == "__main__":
    main()

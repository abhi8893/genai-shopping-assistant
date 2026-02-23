#!/usr/bin/env python3
"""Wrapper script to build uv lockfiles locally or inside a linux/amd64 container."""

import argparse
import platform
import subprocess
import sys
from pathlib import Path


def get_native_container_platform() -> str:
    """Return the native linux container platform for the current host."""
    machine = platform.machine()
    if machine in ("arm64", "aarch64"):
        return "linux/arm64"
    if machine in ("x86_64", "amd64"):
        return "linux/amd64"

    return f"linux/{machine}"


def build_local(repo_root: Path, component: str | None, all_components: bool) -> int:
    """Execute build_venv_lockfile_local.py directly."""
    script = Path(__file__).parent / "build_venv_lockfile_local.py"
    cmd = ["python3", str(script), "--repo-root", str(repo_root)]

    if all_components:
        cmd.append("--all-components")
    else:
        cmd.extend(["--component", component])

    result = subprocess.run(cmd, check=False)
    return result.returncode


def build_linux_amd64(
    repo_root: Path, component: str | None, all_components: bool
) -> int:
    """Build a linux/amd64 container image and execute the lockfile script inside it."""
    image_tag = "uv-venv-builder:latest"
    dockerfile = "scripts/Dockerfile.lockfile"

    print("Creating uv venv builder image...")
    build_result = subprocess.run(
        [
            "podman",
            "buildx",
            "build",
            ".",
            f"--platform={get_native_container_platform()}",
            "-t",
            image_tag,
            "-f",
            dockerfile,
        ],
        check=False,
        cwd=repo_root,
    )

    if build_result.returncode != 0:
        print("Error: Failed to build container image.", file=sys.stderr)
        return build_result.returncode

    script_cmd = "python3 scripts/build_venv_lockfile_local.py --repo-root /workspace"
    if all_components:
        script_cmd += " --all-components"
    else:
        script_cmd += f" --component {component}"

    run_result = subprocess.run(
        [
            "podman",
            "run",
            f"--platform={get_native_container_platform()}",
            "--rm",
            "-v",
            f"{repo_root}:/workspace",
            "-w",
            "/workspace",
            image_tag,
            "bash",
            "-c",
            script_cmd,
        ],
        check=False,
    )

    return run_result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build uv lockfiles for monorepo components (local or linux/amd64)"
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

    parser.add_argument(
        "--build-mode",
        choices=["local", "linux/amd64"],
        default="linux/amd64",
        help=(
            "Build mode: 'local' runs directly, 'linux/amd64' "
            "builds and runs inside a container (default: linux/amd64)"
        ),
    )

    args = parser.parse_args()
    repo_root = Path(args.repo_root)

    if args.build_mode == "local":
        return build_local(repo_root, args.component, args.all_components)

    return build_linux_amd64(repo_root, args.component, args.all_components)


if __name__ == "__main__":
    sys.exit(main())

import contextlib
import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

_HERE = Path(__file__).parent
LOCKFILE_DOCKERFILE = _HERE / "Dockerfile.lockfile"


class StatusCode(Enum):
    SUCCESS = 0
    FAILED = 1
    SKIPPED = 2


@dataclass
class Status:
    code: StatusCode
    reason: str | None = None


def get_native_container_platform() -> str:
    machine = platform.machine()
    if machine in ("arm64", "aarch64"):
        return "linux/arm64"
    if machine in ("x86_64", "amd64"):
        return "linux/amd64"
    return f"linux/{machine}"


def build_lockfile_local(component_path: Path) -> Status:
    if not (component_path / "pyproject.toml").exists():
        return Status(StatusCode.SKIPPED)
    try:
        subprocess.run(["uv", "lock"], cwd=component_path, check=True)
        return Status(StatusCode.SUCCESS)
    except subprocess.CalledProcessError as e:
        return Status(
            StatusCode.FAILED, f"Error building lockfile for {component_path}: {e}"
        )


def build_lockfile_container(
    repo_root: Path, component: str | None, all_components: bool
) -> Status:
    image_tag = "uv-venv-builder:latest"

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
            LOCKFILE_DOCKERFILE,
        ],
        check=False,
        cwd=repo_root,
    )
    if build_result.returncode != 0:
        return Status(
            StatusCode.FAILED, f"Process failed with code {build_result.returncode}"
        )

    script_cmd = "project venv lockfile"
    if all_components:
        script_cmd += " --all"
    elif component:
        script_cmd += f" {component}"

    # NOTE: In container we probably just want to mount and run `uv lock` directly
    # but maintaining compatibility with original podman execution:
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
    return (
        Status(StatusCode.SUCCESS)
        if run_result.returncode == 0
        else Status(
            StatusCode.FAILED, f"Process failed with code {run_result.returncode}"
        )
    )


def venv_exists(repo_root: Path, component: str, group: str) -> bool:
    component_path = repo_root if component == "root" else repo_root / component
    venv_name = f".venv-{group}"
    if (component_path / venv_name).exists():
        return True
    info_file = component_path / ".info.json"
    if (component_path / ".venv").exists() and info_file.exists():
        with contextlib.suppress(Exception):
            data = json.loads(info_file.read_text())
            if data.get("venv", {}).get("active") == venv_name:
                return True
    return False


def update_info_json(component_path: Path) -> None:
    info_file = component_path / ".info.json"
    data = {"venv": {"options": [], "active": None}}
    if info_file.exists():
        with contextlib.suppress(Exception):
            data = json.loads(info_file.read_text())

    venv_available = [
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    ]
    data.setdefault("venv", {})
    data["venv"]["options"] = sorted(venv_available)
    info_file.write_text(json.dumps(data, indent=4))


def get_path_dependencies(component_path: Path) -> list[tuple[str, Path]]:
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
                dep_path = (component_path / dep_config["path"]).resolve()
                path_deps.append((dep_name, dep_path))
        return path_deps
    except Exception as e:
        print(f"Warning: Could not parse pyproject.toml: {e}", file=sys.stderr)
        return []


def _install_venv_dependencies(
    component_path: Path, venv_name: str, group: str
) -> Status:
    try:
        if group == "dev":
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
            path_deps = get_path_dependencies(component_path)
            for _dep_name, dep_path in path_deps:
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
            subprocess.run(
                ["uv", "pip", "install", "--python", venv_name, "."],
                cwd=component_path,
                check=True,
            )
        else:
            subprocess.run(
                ["uv", "pip", "install", "--python", venv_name, ".", "--group", group],
                cwd=component_path,
                check=True,
            )
        return Status(StatusCode.SUCCESS)
    except subprocess.CalledProcessError as e:
        return Status(StatusCode.FAILED, f"Error installing dependencies: {e}")


def create_venv(
    repo_root: Path, component: str, group: str, overwrite: bool = False
) -> Status:
    component_path = repo_root if component == "root" else repo_root / component
    if not component_path.exists():
        return Status(StatusCode.SKIPPED)

    venv_name = f".venv-{group}" if group not in ("dev", "prod") else f".venv-{group}"

    info_file = component_path / ".info.json"
    was_active = False
    if info_file.exists():
        with contextlib.suppress(Exception):
            data = json.loads(info_file.read_text())
            current_active = data.get("venv", {}).get("active")
            if current_active == venv_name:
                was_active = True
                if not overwrite:
                    return Status(
                        StatusCode.SKIPPED, f"Group {group} venv already exists"
                    )

                unswitch_venv(repo_root, component)

    print(f"Creating virtual environment for {component}...")

    cmd = ["uv", "venv", venv_name, "--prompt", f"{component}@{group}"]
    if overwrite:
        cmd.append("--clear")

    try:
        subprocess.run(cmd, cwd=component_path, check=True)
    except subprocess.CalledProcessError as e:
        return Status(StatusCode.FAILED, f"Error creating venv: {e}")

    print(f"Installing {component} dependencies...")
    status = _install_venv_dependencies(component_path, venv_name, group)
    if status.code != StatusCode.SUCCESS:
        return status

    update_info_json(component_path)

    if was_active:
        switch_venv(repo_root, component, group)
    return Status(StatusCode.SUCCESS)


def _update_clean_info(
    info_file: Path,
    component_path: Path,
    clear_info: bool,
    group: str | None,
    current_active: str | None,
) -> None:
    if not info_file.exists():
        return
    if clear_info:
        data = {"venv": {"options": [], "active": None}}
    else:
        data = {"venv": {}}
        with contextlib.suppress(Exception):
            data = json.loads(info_file.read_text())
        data.setdefault("venv", {})
        data["venv"]["options"] = sorted(
            [os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))]
        )
        venv_name = f".venv-{group}" if group else None
        # If cleaning all venvs (group is None), clear active
        # If cleaning specific group and it's the active one, clear active
        if (not group and current_active) or (group and current_active == venv_name):
            data["venv"]["active"] = None
    info_file.write_text(json.dumps(data, indent=4))


def clean_venvs(
    repo_root: Path, component: str, group: str | None = None, clear_info: bool = False
) -> Status:
    component_path = repo_root if component == "root" else repo_root / component
    if not component_path.exists():
        return Status(StatusCode.SKIPPED)

    info_file = component_path / ".info.json"
    current_active = None
    if info_file.exists():
        with contextlib.suppress(Exception):
            current_active = (
                json.loads(info_file.read_text()).get("venv", {}).get("active")
            )

    cleaned = False
    venv_name = f".venv-{group}" if group else None
    if group:
        venv_path = (
            component_path / ".venv"
            if current_active == venv_name
            else component_path / venv_name
        )
        if venv_path.exists() and venv_path.is_dir():
            shutil.rmtree(venv_path)
            cleaned = True
    else:
        for venv_dir in list(component_path.glob(".venv*")):
            if venv_dir.is_dir():
                shutil.rmtree(venv_dir)
                cleaned = True

    _update_clean_info(info_file, component_path, clear_info, group, current_active)

    if not cleaned:
        return Status(StatusCode.SKIPPED)
    return Status(StatusCode.SUCCESS)


def repair_venv_references(venv_dir: Path, dry_run: bool = False) -> Status:
    venv_dir = venv_dir.resolve()
    if not venv_dir.exists():
        return Status(StatusCode.SKIPPED)
    bin_dir = venv_dir / "bin"
    if not bin_dir.exists():
        return Status(StatusCode.SKIPPED)

    parent = re.escape(str(venv_dir.parent))
    pattern = re.compile(rf"{parent}/\.venv(?:-[a-zA-Z0-9_-]*)?")
    replacement = str(venv_dir)

    updated = 0
    for file_path in bin_dir.iterdir():
        if not file_path.is_file():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        new_content = pattern.sub(replacement, content)
        if new_content != content:
            if not dry_run:
                file_path.write_text(new_content, encoding="utf-8")
            updated += 1

    if updated == 0:
        return Status(StatusCode.SKIPPED)
    return Status(StatusCode.SUCCESS)


def switch_venv(repo_root: Path, component: str, target_venv: str) -> Status:
    component_path = repo_root if component == "root" else repo_root / component
    if not component_path.exists():
        return Status(StatusCode.SKIPPED)

    target_venv = (
        f".venv-{target_venv}" if not target_venv.startswith(".venv-") else target_venv
    )
    info_file = component_path / ".info.json"
    default_venv = component_path / ".venv"
    target_venv_path = component_path / target_venv

    if not info_file.exists():
        return Status(StatusCode.SKIPPED)

    data = json.loads(info_file.read_text())
    current_active = data.get("venv", {}).get("active")

    if current_active == target_venv:
        if default_venv.exists():
            return Status(StatusCode.SUCCESS)
    elif not target_venv_path.exists():
        return Status(StatusCode.FAILED)

    if current_active and default_venv.exists():
        default_venv.rename(component_path / current_active)
    elif default_venv.exists():
        shutil.rmtree(default_venv)

    if not target_venv_path.exists():
        return Status(StatusCode.FAILED)

    target_venv_path.rename(default_venv)
    repair_venv_references(default_venv)

    all_venvs = {
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    }
    all_venvs.add(target_venv)
    data["venv"]["options"] = sorted(all_venvs)
    data["venv"]["active"] = target_venv
    info_file.write_text(json.dumps(data, indent=4))
    return Status(StatusCode.SUCCESS)


def unswitch_venv(repo_root: Path, component: str) -> Status:
    component_path = repo_root if component == "root" else repo_root / component
    info_file = component_path / ".info.json"
    default_venv = component_path / ".venv"
    if not info_file.exists():
        return Status(StatusCode.SKIPPED)

    data = json.loads(info_file.read_text())
    current_active = data.get("venv", {}).get("active")
    if not current_active:
        return Status(StatusCode.SUCCESS)
    if not default_venv.exists():
        return Status(StatusCode.FAILED)

    target_venv_path = component_path / current_active
    if target_venv_path.exists():
        shutil.rmtree(target_venv_path)

    default_venv.rename(target_venv_path)
    repair_venv_references(target_venv_path)

    data["venv"]["options"] = sorted(
        [os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))]
    )
    data["venv"]["active"] = None
    info_file.write_text(json.dumps(data, indent=4))
    return Status(StatusCode.SUCCESS)


def _write_refreshed_info(
    info_file: Path, data: dict, component: str, is_valid: bool, fix_active: bool
) -> Status:
    if not is_valid:
        print(f"Warning: {component} has invalid active venv state", file=sys.stderr)
        if fix_active:
            print("Fixing state...", file=sys.stderr)
            data["venv"]["active"] = None

    new_content = json.dumps(data, indent=4)
    if info_file.exists():
        old_content = info_file.read_text()
        if old_content == new_content:
            if not is_valid and not fix_active:
                return Status(StatusCode.SUCCESS)
            return Status(StatusCode.SKIPPED)

    info_file.write_text(new_content)
    return Status(StatusCode.SUCCESS)


def refresh_info_json(
    repo_root: Path, component: str, fix_active: bool = False
) -> Status:
    component_path = repo_root if component == "root" else repo_root / component
    info_file = component_path / ".info.json"
    venv_available = [
        os.path.basename(f) for f in glob.glob(str(component_path / ".venv-*"))
    ]

    data = {"venv": {"options": [], "active": None}}
    if info_file.exists():
        with contextlib.suppress(Exception):
            data = json.loads(info_file.read_text())

    current_active = data.get("venv", {}).get("active")
    all_venvs = set(venv_available)
    if current_active and current_active.startswith(".venv-"):
        all_venvs.add(current_active)
    data.setdefault("venv", {})
    data["venv"]["options"] = sorted(all_venvs)

    default_venv_exists = (component_path / ".venv").exists()
    is_valid = True
    if current_active and (
        current_active == ".venv"
        or (current_active.startswith(".venv-") and current_active in venv_available)
        or (current_active.startswith(".venv-") and not default_venv_exists)
        or not current_active.startswith(".venv-")
    ):
        is_valid = False

    return _write_refreshed_info(info_file, data, component, is_valid, fix_active)


def get_venv_info(repo_root: Path, component: str) -> tuple[str, str]:
    component_path = repo_root if component == "root" else repo_root / component
    info_file = component_path / ".info.json"
    if not info_file.exists():
        return "null", ""
    try:
        data = json.loads(info_file.read_text())
        venv = data.get("venv", {})
        return venv.get("active") or "null", ", ".join(venv.get("options", []))
    except Exception:
        return "null", ""

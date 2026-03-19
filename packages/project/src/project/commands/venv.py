from pathlib import Path

import click

from project.core.components import list_components
from project.core.utils import get_repo_root
from project.core.venv import (
    Status,
    StatusCode,
    build_lockfile_container,
    build_lockfile_local,
    clean_venvs,
    create_venv,
    get_venv_info,
    refresh_info_json,
    repair_venv_references,
    switch_venv,
    unswitch_venv,
    venv_exists,
)


def get_target_components(
    repo_root: Path, component: str | None, all_flag: bool
) -> list[str]:
    if all_flag:
        components = list_components(repo_root)
    else:
        if component is None:
            raise click.UsageError("Must specify COMPONENT or --all")
        components = [component]

    return components


def _show():
    repo_root = get_repo_root()
    components = list_components(repo_root)

    rows = [(c, *get_venv_info(repo_root, c)) for c in components]
    headers = ("COMPONENT", "ACTIVE", "OPTIONS")
    col_widths = [
        max(len(headers[i]), max((len(row[i]) for row in rows), default=0))
        for i in range(3)
    ]

    def fmt_row(cols):
        return "  ".join(
            col.ljust(col_widths[i]) for i, col in enumerate(cols)
        ).rstrip()

    click.echo("\n" + fmt_row(headers))
    click.echo("  ".join("-" * w for w in col_widths))
    for row in rows:
        click.echo(fmt_row(row))


def print_summary_table(command_name: str, results: list[tuple[str, Status]]):
    """Print a tabular summary of command execution results."""
    click.echo(f"\n=== {command_name.upper()} SUMMARY ===\n")

    headers = ("COMPONENT", "STATUS", "REASON")
    max_comp_len = (
        max([len(r[0]) for r in results] + [len(headers[0])])
        if results
        else len(headers[0])
    )

    click.echo(
        f"{headers[0].ljust(max_comp_len)} | {headers[1].ljust(12)} | {headers[2]}"
    )
    click.echo("-" * (max_comp_len + 30))

    failed = False
    for comp, status in results:
        reason_text = status.reason or ""
        if status.code == StatusCode.SUCCESS:
            status_text = "✓ SUCCESS".ljust(12)
            color = "green"
        elif status.code == StatusCode.SKIPPED:
            status_text = ":: SKIPPED".ljust(12)
            color = "yellow"
        else:
            status_text = "✗ FAILED".ljust(12)
            color = "red"

        click.echo(f"{comp.ljust(max_comp_len)} | ", nl=False)
        click.secho(status_text, fg=color, nl=False)
        click.echo(f" | {reason_text}" if reason_text else "")

        if status.code == StatusCode.FAILED:
            failed = True

    _show()

    if failed:
        raise click.exceptions.Exit(1)


@click.group(name="venv")
def venv_cli():
    """Virtual environment management commands."""
    pass


@venv_cli.command(name="create")
@click.argument("component", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Create venvs for all components")
@click.option(
    "--group", default="prod", help="Dependency group (dev, prod, test, etc.)"
)
@click.option(
    "--overwrite", is_flag=True, help="Overwrite existing virtual environments"
)
@click.option(
    "--missing-only", is_flag=True, help="Only create venv if it doesn't already exist"
)
def create(
    component: str | None,
    all_flag: bool,
    group: str,
    overwrite: bool,
    missing_only: bool,
):
    """Create virtual environment for monorepo component(s)."""
    repo_root = get_repo_root()
    targets = get_target_components(repo_root, component, all_flag)

    results = []
    for target in targets:
        if missing_only and venv_exists(repo_root, target, group):
            results.append(
                (
                    target,
                    Status(StatusCode.SKIPPED, f"Group {group} venv already exists"),
                )
            )
            continue

        click.echo(f"\n==> Creating venv for {target} (GROUP={group})...")
        status = create_venv(repo_root, target, group, overwrite)
        results.append((target, status))
    print_summary_table("CREATE", results)


@venv_cli.command(name="clean")
@click.argument("component", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Clean venvs for all components")
@click.option("--group", help="Specific venv group to clean")
@click.option("--clear-info", is_flag=True, help="Clear all venv info in .info.json")
@click.option("--include-root", is_flag=True, help="Include the root component")
def clean(
    component: str | None,
    all_flag: bool,
    group: str | None,
    clear_info: bool,
    include_root: bool,
):
    """Clean virtual environments for monorepo component(s)."""

    if component == "root":
        include_root = True

    repo_root = get_repo_root()
    targets = get_target_components(repo_root, component, all_flag)

    results = []
    for target in targets:
        if target == "root" and not include_root:
            results.append((target, Status(StatusCode.SKIPPED)))
            continue

        click.echo(f"\n==> Cleaning venv for {target}...")
        status = clean_venvs(repo_root, target, group, clear_info)
        results.append((target, status))
    print_summary_table("CLEAN", results)


@venv_cli.command(name="switch")
@click.argument("component", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Switch venvs for all components")
@click.option("--target", required=True, help="Target venv to switch to")
@click.option("--include-root", is_flag=True, help="Include the root component")
def switch(component: str | None, all_flag: bool, target: str, include_root: bool):
    """Switch active virtual environment for monorepo component(s)."""

    if component == "root":
        include_root = True

    repo_root = get_repo_root()
    targets = get_target_components(repo_root, component, all_flag)

    results = []
    for comp in targets:
        if comp == "root" and not include_root:
            results.append((comp, Status(StatusCode.SKIPPED)))
            continue

        click.echo(f"\n==> Switching venv for {comp} (TARGET={target})...")
        status = switch_venv(repo_root, comp, target)
        results.append((comp, status))
    print_summary_table("SWITCH", results)


@venv_cli.command(name="unswitch")
@click.argument("component", required=False)
@click.option(
    "--all", "all_flag", is_flag=True, help="Unswitch venvs for all components"
)
@click.option("--include-root", is_flag=True, help="Include the root component")
def unswitch(component: str | None, all_flag: bool, include_root: bool):
    """Deactivate (unswitch) virtual environment for monorepo component(s)."""

    if component == "root":
        include_root = True

    repo_root = get_repo_root()
    targets = get_target_components(repo_root, component, all_flag)

    results = []
    for target in targets:
        if target == "root" and not include_root:
            results.append((target, Status(StatusCode.SKIPPED)))
            continue

        click.echo(f"\n==> Unswitching venv for {target}...")
        status = unswitch_venv(repo_root, target)
        results.append((target, status))
    print_summary_table("UNSWITCH", results)


@venv_cli.command(name="refresh")
@click.argument("component", required=False)
@click.option(
    "--all", "all_flag", is_flag=True, help="Refresh .info.json for all components"
)
@click.option("--fix", "fix_flag", is_flag=True, help="Automatically fix invalid state")
def refresh(component: str | None, all_flag: bool, fix_flag: bool):
    """Refresh .info.json for monorepo component(s)."""
    repo_root = get_repo_root()
    targets = get_target_components(repo_root, component, all_flag)

    results = []
    for target in targets:
        click.echo(f"\n==> Refreshing {target}...")
        status = refresh_info_json(repo_root, target, fix_flag)
        results.append((target, status))
    print_summary_table("REFRESH", results)


@venv_cli.command(name="repair-refs")
@click.argument("component", required=False)
@click.option(
    "--all", "all_flag", is_flag=True, help="Repair venv scripts for all components"
)
def repair_refs(component: str | None, all_flag: bool):
    """Repair stale VIRTUAL_ENV path references in venv activate scripts."""
    repo_root = get_repo_root()
    targets = get_target_components(repo_root, component, all_flag)

    results = []
    for target in targets:
        click.echo(f"\n==> Repairing venv refs for {target}...")
        comp_dir = repo_root if target == "root" else repo_root / target
        status = repair_venv_references(comp_dir / ".venv")
        results.append((target, status))
    print_summary_table("REPAIR REFS", results)


@venv_cli.command(name="show")
def show():
    """Show active venvs for all components."""
    _show()


@venv_cli.command(name="lockfile")
@click.argument("component", required=False)
@click.option(
    "--all", "all_flag", is_flag=True, help="Build lockfiles for all components"
)
@click.option(
    "--build-mode", default="linux/amd64", type=click.Choice(["local", "linux/amd64"])
)
def lockfile(component: str | None, all_flag: bool, build_mode: str):
    """Build uv lockfiles for monorepo component(s)."""
    repo_root = get_repo_root()
    if not component and not all_flag:
        raise click.UsageError("Must specify COMPONENT or --all")

    if build_mode == "local":
        if all_flag:
            targets = list_components(repo_root)
            results = []
            for target in targets:
                comp_dir = repo_root if target == "root" else repo_root / target
                status = build_lockfile_local(comp_dir)
                results.append((target, status))
            print_summary_table("LOCKFILE", results)
        else:
            comp_dir = repo_root if component == "root" else repo_root / str(component)
            status = build_lockfile_local(comp_dir)
            print_summary_table("LOCKFILE", [(str(component), status)])
    else:
        status = build_lockfile_container(repo_root, component, all_flag)
        if status != 0:
            raise click.exceptions.Exit(status)

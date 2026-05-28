import sys

import click
from tabulate import tabulate

from project.core.utils import get_repo_root
from project.core.version import (
    ALL_COMPONENTS,
    bump_versions,
    compare_versions,
    get_release_info,
    get_version_info,
)


@click.group(name="version")
def version_cli():
    """Manage project versioning."""
    pass


@version_cli.command()
def get():
    """Get the current version and release type."""
    repo_root = get_repo_root()
    try:
        info = get_version_info(repo_root)
        click.echo(f"VERSION: {info.version}")
        click.echo(f"RELEASE_TYPE: {info.release_type}")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)


@version_cli.command()
@click.argument("new_version")
@click.argument("old_version")
@click.option(
    "--no-enforce-unit-bump",
    is_flag=True,
    help="Do not enforce single unit bump restriction",
)
def compare(new_version: str, old_version: str, no_enforce_unit_bump: bool):
    """Assert new_version > old_version using semver semantics."""
    try:
        result = compare_versions(
            new_version, old_version, enforce_unit_bump=not no_enforce_unit_bump
        )
        if not result:
            click.secho(
                f"Error: Version {new_version} must be greater than {old_version}",  # noqa: E501
                fg="red",
            )
            sys.exit(1)
        click.echo(f"✓ {new_version} > {old_version}")
    except ValueError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)


@version_cli.command(name="release-info")
@click.argument("branch")
@click.option("--test-release", is_flag=True, help="Test release mode")
def release_info_cmd(branch: str, test_release: bool):
    """Determine release info based on current branch."""
    repo_root = get_repo_root()
    try:
        info = get_release_info(branch, repo_root, test_release)
        click.echo(f"VERSION={info.version}")
        click.echo(f"TAG_NAME={info.tag_name}")
        click.echo(f"RELEASE_TYPE={info.release_type}")
        click.echo(f"RELEASE_BRANCH={info.release_branch}")
        click.echo(f"TEST_RELEASE={info.test_release}")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)


@version_cli.command()
@click.option(
    "--component",
    multiple=True,
    type=click.Choice(ALL_COMPONENTS),
    help="Component to bump version",
)
@click.option(
    "--part",
    required=True,
    type=click.Choice(["major", "minor", "patch", "prerelease", "build", "stable"]),
    help="Version part to bump",
)
@click.option("--prerelease-prefix", help="Prerelease prefix (e.g., rc, dev)")
@click.option("--allow-downgrade", is_flag=True, help="Allow downgrading version")
def bump(
    component: tuple[str, ...],
    part: str,
    prerelease_prefix: str | None,
    allow_downgrade: bool,
):
    """Bump version across monorepo components."""
    repo_root = get_repo_root()
    try:
        versions_components = bump_versions(
            repo_root=repo_root,
            part=part,
            prerelease_prefix=prerelease_prefix,
            allow_downgrade=allow_downgrade,
            target_components=list(component) if component else None,
        )

        # Print summary
        rows = []
        for comp, files in versions_components.items():
            for fpath, v_info in files.items():
                rows.append([comp, fpath, v_info["current"], v_info["new"]])

        if not rows:
            click.echo("No versions found.")
            return

        headers = ["Component", "File", "Current Version", "New Version"]
        click.echo(f"\\n{tabulate(rows, headers=headers, tablefmt='github')}\\n")

        click.secho("=" * 80, fg="green")
        click.secho("Version bumped successfully", fg="green")
        click.secho("=" * 80, fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)

from pathlib import Path

import click

from project.core.components import list_components


def get_repo_root() -> Path:
    return Path.cwd()


@click.group(name="components")
def components_cli():
    """Component discovery commands."""
    pass


@components_cli.command(name="list")
def list_cmd():
    """List all components in the monorepo with pyproject.toml."""
    repo_root = get_repo_root()
    components = list_components(repo_root)

    for component in components:
        click.echo(component)

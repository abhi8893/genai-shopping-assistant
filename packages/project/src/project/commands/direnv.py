import click

from project.core.components import list_components
from project.core.direnv import setup_direnv
from project.core.utils import get_repo_root


@click.group(name="direnv")
def direnv_cli():
    """Direnv integration commands."""
    pass


@direnv_cli.command(name="setup")
def setup():
    """Setup .envrc files for direnv auto-activation."""
    repo_root = get_repo_root()
    components = list_components(repo_root)

    click.echo("Setting up .envrc files...")
    results = setup_direnv(repo_root, components)

    for res in results:
        # root -> . (root) for output matching old script
        name = ". (root)" if res == "root" else res
        click.echo(f"  ✓ {name}")

    click.echo("\n✓ .envrc files created and allowed")

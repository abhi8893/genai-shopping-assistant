import click

from project.commands.components import components_cli
from project.commands.direnv import direnv_cli
from project.commands.venv import venv_cli


@click.group()
def main():
    """Project Monorepo Management CLI."""
    pass


main.add_command(venv_cli)
main.add_command(direnv_cli)
main.add_command(components_cli)

if __name__ == "__main__":
    main()

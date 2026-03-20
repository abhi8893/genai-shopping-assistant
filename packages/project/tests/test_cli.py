from click.testing import CliRunner
from project.cli import main

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Project Monorepo Management CLI" in result.output

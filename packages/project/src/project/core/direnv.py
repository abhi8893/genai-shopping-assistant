import subprocess
from pathlib import Path

ENVRC_TEMPLATE = """\
if [ -d ".venv" ]; then
  export VIRTUAL_ENV_DISABLE_PROMPT=1
  source .venv/bin/activate
else
  echo "direnv: no .venv found, run: make venv-create COMPONENT={component} GROUP=dev"
fi
"""

ROOT_ENVRC = """\
if [ -d ".venv" ]; then
  export VIRTUAL_ENV_DISABLE_PROMPT=1
  source .venv/bin/activate
else
  echo "direnv: no .venv found at project root"
fi
"""


def write_envrc(path: Path, content: str) -> None:
    (path / ".envrc").write_text(content)
    subprocess.run(["direnv", "allow"], cwd=str(path), check=True, capture_output=True)


def setup_direnv(repo_root: Path, components: list[str]) -> list[str]:
    """Setup .envrc files for all components."""
    results = []

    write_envrc(repo_root, ROOT_ENVRC)
    results.append("root")

    for component in components:
        if component == "root":
            continue
        write_envrc(repo_root / component, ENVRC_TEMPLATE.format(component=component))
        results.append(component)

    return results

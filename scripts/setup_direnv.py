#!/usr/bin/env python3
"""Generate .envrc files for direnv auto-activation with custom venv prompt names."""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from list_components import list_components

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


def main():
    parser = argparse.ArgumentParser(
        description="Generate .envrc files for direnv auto-activation"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)

    write_envrc(repo_root, ROOT_ENVRC)
    print("  ✓ . (root)")

    for component in list_components(repo_root):
        write_envrc(repo_root / component, ENVRC_TEMPLATE.format(component=component))
        print(f"  ✓ {component}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

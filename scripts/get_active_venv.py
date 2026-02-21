#!/usr/bin/env python3
"""Script to display venv status (active + options) for all monorepo components."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from list_components import list_components  # noqa: E402


def get_venv_info(repo_root: Path, component: str) -> tuple[str, str]:
    """Return (active, options_str) for a component from its .info.json."""
    info_file = repo_root / component / ".info.json"
    if not info_file.exists():
        return "null", ""

    with open(info_file) as f:
        data = json.load(f)

    venv = data.get("venv", {})
    active = venv.get("active") or "null"
    options = ", ".join(venv.get("options", []))
    return active, options


def main():
    parser = argparse.ArgumentParser(
        description="Display venv status for all monorepo components"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    components = list_components(repo_root)

    rows = [(c, *get_venv_info(repo_root, c)) for c in components]

    # Calculate column widths
    headers = ("COMPONENT", "ACTIVE", "OPTIONS")
    col_widths = [
        max(len(headers[i]), max((len(row[i]) for row in rows), default=0))
        for i in range(3)
    ]

    def fmt_row(cols):
        return "  ".join(
            col.ljust(col_widths[i]) for i, col in enumerate(cols)
        ).rstrip()

    print(fmt_row(headers))
    print("  ".join("-" * w for w in col_widths))
    for row in rows:
        print(fmt_row(row))

    return 0


if __name__ == "__main__":
    sys.exit(main())

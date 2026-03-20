from pathlib import Path


def get_repo_root() -> Path:
    """Find the repo root by assuming the cwd is inside the monorepo."""
    return Path.cwd()

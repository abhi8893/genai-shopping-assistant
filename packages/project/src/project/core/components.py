from pathlib import Path


def list_components(repo_root: Path) -> list[str]:
    """Find all components with pyproject.toml files."""
    components = ["root"]
    search_dirs = ["packages", "services"]

    for search_dir in search_dirs:
        search_path = repo_root / search_dir
        if not search_path.exists():
            continue

        for pyproject_file in search_path.rglob("pyproject.toml"):
            if any(part.startswith(".venv") for part in pyproject_file.parts):
                continue
            component_path = pyproject_file.parent.relative_to(repo_root)
            components.append(str(component_path))

    return [components[0]] + sorted(components[1:])

import argparse
import re
from pathlib import Path

import semver
from tabulate import tabulate

COMPONENT_FILE_CONFIG = {
    "root": {
        "pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
    "packages/shopping-assistant": {
        "packages/shopping-assistant/pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
    "services/shopping-assistant": {
        "services/shopping-assistant/pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
    "services/ecom-backend": {
        "services/ecom-backend/pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
}

ALL_COMPONENTS = list(COMPONENT_FILE_CONFIG.keys())
SEMVER_PRERELEASE_DEFAULT = "rc"


def bump_part(
    version: semver.Version, part: str, prerelease: str | None = None
) -> semver.Version:
    if (
        (part == "prerelease")
        and (version.prerelease is None)
        and (prerelease != SEMVER_PRERELEASE_DEFAULT)
    ):
        version_dict = version.to_dict()
        version_dict["prerelease"] = f"{prerelease}0"
        next_version = semver.Version(**version_dict)
    else:
        next_version = version.next_version(part=part)

    return next_version


def parse_version_from_file(
    fpath: str,
    pattern: str,
) -> semver.Version:
    # open file (utf-8)
    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    # find pattern
    pattern = re.compile(pattern)
    matches = pattern.search(content)

    if not matches:
        raise ValueError(f"Pattern {pattern} not found in {fpath}")

    # get versions matching pattern
    versions = [semver.Version.parse(matches.group("version"))]
    if len(versions) != 1:
        raise ValueError(f"Multiple versions found in {fpath}")
    return versions[0]


def replace_version_in_file(
    fpath: str,
    pattern: str,
    new_version: semver.Version,
) -> None:
    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(pattern)
    new_content = pattern.sub(
        lambda m: f"{m.group(1)}{new_version}{m.group(3)}", content
    )
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return new_content


def change_version(
    fpath: str,
    pattern: str,
    new_version: semver.Version,
) -> dict[str, semver.Version]:
    # replace versions in file
    replace_version_in_file(fpath=fpath, pattern=pattern, new_version=new_version)


def show_file_version_summary(
    version_components: dict, version_types: list[str]
) -> None:
    """
    Pretty print component version summary table.
    """

    rows = []

    for component, files in version_components.items():
        for fpath, version_info in files.items():
            lst = [component, fpath]
            for version_type in version_types:
                lst.append(version_info[version_type])
            rows.append(lst)

    if not rows:
        print("No versions found.")
        return

    headers = ["Component", "File"]
    headers += [
        f"{version_type.capitalize()} Version" for version_type in version_types
    ]

    print()
    print(
        tabulate(
            rows,
            headers=headers,
            tablefmt="github",  # clean in CI logs
        )
    )


def validate_versions(
    versions_components: dict,
    version_types: list[str],
) -> dict[str, bool]:
    """
    Validate that within each component, all files share the same version
    for each specified version_type (e.g. current, new).

    Prints a pivoted summary table showing:
        {version_value(s)} ({OK | MISMATCH})

    Returns:
        {component: bool}
    """

    rows = []
    validation_status = {}

    # Dynamic headers
    headers = ["Component"] + [
        f"Status ({vt.capitalize()} Version)" for vt in version_types
    ]

    for component, files in versions_components.items():
        component_valid = True
        row = [component]

        for version_type in version_types:
            values = [
                str(file_info.get(version_type))
                for file_info in files.values()
                if version_type in file_info
            ]

            unique_values = sorted(set(values))

            is_consistent = len(unique_values) <= 1
            if not is_consistent:
                component_valid = False

            if not unique_values:
                cell_value = "N/A"
            else:
                version_display = ", ".join(unique_values)
                status_display = "OK" if is_consistent else "MISMATCH"
                cell_value = f"{version_display} ({status_display})"

            row.append(cell_value)

        validation_status[component] = component_valid
        rows.append(row)

    print()
    print(tabulate(rows, headers=headers, tablefmt="github"))

    return validation_status


def main():
    parser = argparse.ArgumentParser(description="Bump version in components")
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument(
        "--component",
        required=False,
        nargs="+",
        default=[],
        choices=ALL_COMPONENTS,
        help="Component to bump version",
    )
    parser.add_argument(
        "--part",
        required=True,
        choices=["major", "minor", "patch", "prerelease", "build"],
        help="Version part to bump",
    )
    parser.add_argument(
        "--prerelease",
        required=False,
        default=SEMVER_PRERELEASE_DEFAULT,
        help="Prerelease initialization identifier",
    )

    args = parser.parse_args()
    repo_root = Path(args.repo_root)

    if args.component:
        components = args.component
    else:
        components = ALL_COMPONENTS

    versions_components = {}
    for component in components:
        print(f"Parsing {component} version")
        files = COMPONENT_FILE_CONFIG[component]
        old_versions_files = {}
        for fpath, config in files.items():
            old_version = parse_version_from_file(
                fpath=str(repo_root / fpath), pattern=config["pattern"]
            )
            old_versions_files[fpath] = {
                "current": old_version,
                "new": bump_part(old_version, args.part, args.prerelease),
            }
        versions_components[component] = old_versions_files

    # Print a tabular summary with headers "Component", "File", "Current Version"
    show_file_version_summary(versions_components, version_types=["current", "new"])

    validation_status = validate_versions(
        versions_components, version_types=["current", "new"]
    )

    if not all(validation_status.values()):
        mismatched_components = [
            component for component, valid in validation_status.items() if not valid
        ]
        raise ValueError(
            "Version mismatch detected in components: "
            + ", ".join(mismatched_components)
        )

    for component, files in versions_components.items():
        for fpath, version_info in files.items():
            pattern = COMPONENT_FILE_CONFIG[component][fpath]["pattern"]
            change_version(
                fpath=str(repo_root / fpath),
                pattern=pattern,
                new_version=version_info["new"],
            )

    print("Version bumped successfully")


if __name__ == "__main__":
    main()

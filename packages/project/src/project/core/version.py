import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

import semver
from project.core.components import list_components

COMPONENT_FILE_CONFIG = {
    "root": {
        "pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
    "packages/project": {
        "packages/project/pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
    "packages/shopping-assistant": {
        "packages/shopping-assistant/pyproject.toml": {
            "pattern": r'(version = ")(?P<version>.+?)(")',
        }
    },
    # TODO: Remove dummy-pkg before release!
    "packages/dummy-pkg": {
        "packages/dummy-pkg/pyproject.toml": {
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
SEMVER_PRERELEASE_PREFIX_DEFAULT = "rc"


@dataclass
class VersionInfo:
    version: str
    release_type: str


@dataclass
class ReleaseInfo:
    version: str
    tag_name: str
    release_type: str
    release_branch: str
    test_release: bool


def get_prerelease_prefix(version: semver.Version) -> str:
    if version.prerelease is None:
        return ""
    return version.prerelease.split(".")[0]


def bump_part(
    version: semver.Version,
    part: str,
    prerelease_prefix: str | None = None,
    allow_downgrade: bool = False,
) -> semver.Version:
    is_prerelease = part == "prerelease"

    if is_prerelease:
        # does a prerelease tag exist
        has_prerelease = version.prerelease is not None

        cur_prerelease_prefix = get_prerelease_prefix(version)

        if not prerelease_prefix:
            if has_prerelease:
                prerelease_prefix = cur_prerelease_prefix
            else:
                prerelease_prefix = SEMVER_PRERELEASE_PREFIX_DEFAULT

        # is provided prerelease prefix same as current one
        is_same_prerelease = cur_prerelease_prefix == prerelease_prefix

        if has_prerelease and is_same_prerelease:
            # increment the prerelease number
            next_version = version.next_version(part="prerelease")
        elif (has_prerelease and not is_same_prerelease) or (not has_prerelease):
            # change the prerelease prefix
            version_dict = version.to_dict()
            version_dict["prerelease"] = f"{prerelease_prefix}.0"
            next_version = semver.Version(**version_dict)
    else:
        next_version = version.next_version(part=part)

    if not allow_downgrade and next_version < version:
        raise ValueError(
            f"Downgrading version from {version} to {next_version} is not allowed. "
            "Set allow_downgrade=True to allow downgrading."
        )
    if next_version == version:
        raise ValueError(f"Version {version} did not get bumped.")

    return next_version


def parse_version_from_file(
    fpath: str | Path,
    pattern: str,
) -> semver.Version:
    # open file (utf-8)
    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    # find pattern
    pat = re.compile(pattern)
    matches = pat.search(content)

    if not matches:
        raise ValueError(f"Pattern {pattern} not found in {fpath}")

    # get versions matching pattern
    versions = [semver.Version.parse(matches.group("version"))]
    if len(versions) != 1:
        raise ValueError(f"Multiple versions found in {fpath}")
    return versions[0]


def replace_version_in_file(
    fpath: str | Path,
    pattern: str,
    new_version: semver.Version,
) -> str:
    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    pat = re.compile(pattern)
    new_content = pat.sub(lambda m: f"{m.group(1)}{new_version}{m.group(3)}", content)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return new_content


def get_version_from_toml(pyproject_toml: str | Path) -> str:
    with open(pyproject_toml, "rb") as f:
        pyproject_toml_content = tomllib.load(f)
        version = pyproject_toml_content["project"]["version"]
    return version


def get_release_type(version: str) -> str:
    ver = semver.Version.parse(version)
    if ver.prerelease:
        if ver.prerelease.startswith("rc."):
            return "rc"
        return "dev"
    return "stable"


def get_version_info(repo_root: Path) -> VersionInfo:
    components = list_components(repo_root)

    versions = {}
    for component in components:
        if component == "root":
            pyproject_toml = repo_root / "pyproject.toml"
        else:
            pyproject_toml = repo_root / component / "pyproject.toml"

        version = get_version_from_toml(pyproject_toml)
        versions[component] = version

    if len(set(versions.values())) != 1:
        mismatch = "\\n".join(f"  {c}: {v}" for c, v in versions.items())
        raise ValueError(
            f"All components must have the same version. Mismatch detected:\\n{mismatch}"  # noqa: E501
        )

    version = versions["root"]
    release_type = get_release_type(version)

    return VersionInfo(version=version, release_type=release_type)


def compare_versions(new_version: str, old_version: str) -> bool:
    try:
        new_ver = semver.Version.parse(new_version)
        old_ver = semver.Version.parse(old_version)
    except ValueError as e:
        raise ValueError(f"Invalid version: {e}") from e

    return new_ver > old_ver


# TODO: Refactor this function to be more modular and testable
def get_release_info(  # noqa: C901
    branch: str, repo_root: Path, test_release: bool = False
) -> ReleaseInfo:
    v_info = get_version_info(repo_root)
    version = v_info.version
    release_type = v_info.release_type
    tag_name = f"v{version}"

    if test_release:
        return ReleaseInfo(version, tag_name, release_type, branch, test_release)

    if branch == "main":
        if release_type != "stable":
            raise ValueError(
                f"Main branch requires stable release type, got: {release_type}"
            )
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version):
            raise ValueError(
                f"Stable release requires X.Y.Z version format, got: {version}"
            )

    elif re.match(r"^release/v[0-9]+\.[0-9]+\.[0-9]+$", branch):
        if release_type != "rc":
            raise ValueError(
                f"Release branch requires rc release type, got: {release_type}"
            )
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+-rc\.[0-9]+$", version):
            raise ValueError(
                f"RC release requires X.Y.Z-rc.N version format, got: {version}"
            )
        base_version = version.split("-rc")[0]
        branch_version = branch.replace("release/v", "")
        if base_version != branch_version:
            raise ValueError(
                f"Version base {base_version} does not match branch version {branch_version}"  # noqa: E501
            )

    elif branch == "develop":
        if release_type != "dev":
            raise ValueError(
                f"Develop branch requires dev release type, got: {release_type}"
            )
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+-dev\.[0-9]+$", version):
            raise ValueError(
                f"Dev release requires X.Y.Z-dev.N version format, got: {version}"
            )

    else:
        raise ValueError(
            f"Releases can only be triggered from develop, release/vX.Y.Z, or main. Current branch: {branch}"  # noqa: E501
        )

    return ReleaseInfo(version, tag_name, release_type, branch, test_release)


def bump_versions(
    repo_root: Path,
    part: str,
    prerelease_prefix: str | None = None,
    allow_downgrade: bool = False,
    target_components: list[str] | None = None,
) -> dict[str, dict[str, dict[str, semver.Version]]]:
    all_found_components = list_components(repo_root)
    missing_components = set(all_found_components) - set(ALL_COMPONENTS)
    extra_components = set(ALL_COMPONENTS) - set(all_found_components)

    if set(all_found_components) != set(ALL_COMPONENTS):
        if missing_components:
            raise ValueError(
                f"Missing version regex config for components: {missing_components}"
            )
        if extra_components:
            raise ValueError(
                f"Extra components specified not present in repo: {extra_components}"
            )

    components = target_components if target_components else ALL_COMPONENTS

    versions_components = {}
    for component in components:
        files = COMPONENT_FILE_CONFIG[component]
        old_versions_files = {}
        for fpath, config in files.items():
            old_version = parse_version_from_file(
                fpath=str(repo_root / fpath), pattern=config["pattern"]
            )
            old_versions_files[fpath] = {
                "current": old_version,
                "new": bump_part(
                    old_version,
                    part,
                    prerelease_prefix,
                    allow_downgrade=allow_downgrade,
                ),
            }
        versions_components[component] = old_versions_files

    # TODO: Check this comment from antigravity
    # Normally we do validations here. I will separate that to CLI printing if needed,
    # or just assume validation logic is okay, but let's implement validation inside
    # the core logic for safety.

    # Validate mismatch
    for component, files in versions_components.items():
        unique_news = {str(file_info["new"]) for file_info in files.values()}
        if len(unique_news) > 1:
            raise ValueError(f"Version mismatch detected in components: {component}")

    # Apply changes
    for component, files in versions_components.items():
        for fpath, version_info in files.items():
            pattern = COMPONENT_FILE_CONFIG[component][fpath]["pattern"]
            replace_version_in_file(
                fpath=str(repo_root / fpath),
                pattern=pattern,
                new_version=version_info["new"],
            )

    return versions_components

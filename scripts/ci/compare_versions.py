# /// script
# requires-python = ">=3.11"
# dependencies = ["semver"]
# ///
"""Assert new_version > old_version using semver semantics.

Supports the project's version formats:
  X.Y.Z         - stable release
  X.Y.Z-devN    - dev pre-release
  X.Y.Z-rcN     - release candidate

Semver ordering: stable > rc > dev (across equal X.Y.Z base)
Examples:
  0.1.0 > 0.1.0-rc1 > 0.1.0-rc0 > 0.1.0-dev1
  0.1.1-dev0 > 0.1.0

Usage:
  uv run scripts/ci/compare_versions.py <new_version> <old_version>
  Exits 0 if new_version > old_version, else exits 1 with an error message.
"""

import argparse

import semver


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assert new_version > old_version using semver semantics."
    )
    parser.add_argument("new_version", help="The new version to validate")
    parser.add_argument("old_version", help="The existing version to compare against")
    args = parser.parse_args()

    new_v, old_v = args.new_version, args.old_version
    try:
        new_ver = semver.Version.parse(new_v)
        old_ver = semver.Version.parse(old_v)
    except ValueError as e:
        raise SystemExit(f"Invalid version: {e}") from e
    if not new_ver > old_ver:
        raise SystemExit(f"Error: Version {new_v} must be greater than {old_v}")
    print(f"✓ {new_v} > {old_v}")


if __name__ == "__main__":
    main()

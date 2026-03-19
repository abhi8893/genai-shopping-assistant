import pytest
from click.testing import CliRunner
from pathlib import Path
import semver

from project.cli import main
from project.core.version import (
    compare_versions,
    get_release_info,
    get_release_type,
    bump_part,
    VersionInfo,
    ReleaseInfo
)

def test_compare_versions():
    assert compare_versions("0.1.0", "0.1.0-rc1") is True
    assert compare_versions("0.1.0-rc1", "0.1.0-rc0") is True
    assert compare_versions("0.1.0-rc0", "0.1.0-dev1") is True
    assert compare_versions("0.1.1-dev0", "0.1.0") is True

    assert compare_versions("0.1.0", "0.1.0") is False
    assert compare_versions("0.1.0", "0.2.0") is False

def test_get_release_type():
    assert get_release_type("0.1.0") == "stable"
    assert get_release_type("1.0.0") == "stable"
    assert get_release_type("0.1.0-rc.0") == "rc"
    assert get_release_type("0.1.0-rc.1") == "rc"
    assert get_release_type("0.1.0-dev.0") == "dev"
    assert get_release_type("0.1.0-dev.5") == "dev"

def test_bump_part():
    v = semver.Version.parse("0.1.0")

    # Major, Minor, Patch
    assert str(bump_part(v, "patch")) == "0.1.1"
    assert str(bump_part(v, "minor")) == "0.2.0"
    assert str(bump_part(v, "major")) == "1.0.0"

    # Prerelease Defaults (Stable to prerelease is a downgrade in semver)
    import pytest
    with pytest.raises(ValueError, match="Downgrading version from"):
        bump_part(v, "prerelease")

    assert str(bump_part(v, "prerelease", allow_downgrade=True)) == "0.1.0-rc.0"
    assert str(bump_part(v, "prerelease", "dev", allow_downgrade=True)) == "0.1.0-dev.0"

    # Prerelease Increment
    v2 = semver.Version.parse("0.1.0-dev.0")
    assert str(bump_part(v2, "prerelease")) == "0.1.0-dev.1"

    # Prerelease Transition
    assert str(bump_part(v2, "prerelease", "rc")) == "0.1.0-rc.0"

def test_get_release_info_stable(monkeypatch):
    # Mock get_version_info
    monkeypatch.setattr("project.core.version.get_version_info", lambda *args: VersionInfo("0.1.0", "stable"))
    info = get_release_info("main", Path("."), False)
    assert info.version == "0.1.0"
    assert info.tag_name == "v0.1.0"
    assert info.release_type == "stable"

def test_get_release_info_rc(monkeypatch):
    monkeypatch.setattr("project.core.version.get_version_info", lambda *args: VersionInfo("0.1.0-rc.1", "rc"))
    info = get_release_info("release/v0.1.0", Path("."), False)
    assert info.version == "0.1.0-rc.1"
    assert info.tag_name == "v0.1.0-rc.1"
    assert info.release_type == "rc"

def test_get_release_info_dev(monkeypatch):
    monkeypatch.setattr("project.core.version.get_version_info", lambda *args: VersionInfo("0.1.0-dev.5", "dev"))
    info = get_release_info("develop", Path("."), False)
    assert info.version == "0.1.0-dev.5"
    assert info.tag_name == "v0.1.0-dev.5"
    assert info.release_type == "dev"

def test_cli_version_get(monkeypatch):
    monkeypatch.setattr("project.commands.version.get_version_info", lambda *args: VersionInfo("0.1.0", "stable"))
    runner = CliRunner()
    result = runner.invoke(main, ["version", "get"])
    assert result.exit_code == 0
    assert "VERSION: 0.1.0" in result.output
    assert "RELEASE_TYPE: stable" in result.output

def test_cli_version_compare():
    runner = CliRunner()
    result = runner.invoke(main, ["version", "compare", "0.2.0", "0.1.0"])
    assert result.exit_code == 0
    assert "✓ 0.2.0 > 0.1.0" in result.output

    result2 = runner.invoke(main, ["version", "compare", "0.1.0", "0.2.0"])
    assert result2.exit_code == 1
    assert "Error: Version 0.1.0 must be greater than 0.2.0" in result2.output

def test_cli_version_release_info(monkeypatch):
    monkeypatch.setattr("project.core.version.get_version_info", lambda *args: VersionInfo("0.1.0", "stable"))
    runner = CliRunner()
    result = runner.invoke(main, ["version", "release-info", "main"])
    assert result.exit_code == 0
    assert "VERSION=0.1.0" in result.output
    assert "RELEASE_TYPE=stable" in result.output

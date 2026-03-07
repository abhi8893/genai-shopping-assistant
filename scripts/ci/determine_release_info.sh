#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-}"
REPO_ROOT="${2:-}"
TEST_RELEASE="${3:-FALSE}"

if [ -z "$BRANCH" ]; then
  echo "Error: branch name argument is required" >&2
  exit 1
fi

if [ -z "$REPO_ROOT" ]; then
  echo "Error: repo root argument is required" >&2
  exit 1
fi

VERSION_OUTPUT=$(python3 scripts/ci/get_version.py --repo-root "$REPO_ROOT")
VERSION=$(echo "$VERSION_OUTPUT" | grep "^VERSION:" | cut -d' ' -f2)
RELEASE_TYPE=$(echo "$VERSION_OUTPUT" | grep "^RELEASE_TYPE:" | cut -d' ' -f2)
TAG_NAME="v${VERSION}"


if [ "$TEST_RELEASE" = "TRUE" ]; then

  echo "VERSION=$VERSION"
  echo "TAG_NAME=$TAG_NAME"
  echo "RELEASE_TYPE=$RELEASE_TYPE"
  echo "RELEASE_BRANCH=$BRANCH"
  echo "TEST_RELEASE=$TEST_RELEASE"
  exit 0
fi

if [ "$BRANCH" = "main" ]; then

  if [ "$RELEASE_TYPE" != "stable" ]; then
    echo "Error: Main branch requires stable release type, got: $RELEASE_TYPE"
    exit 1
  fi
  if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Stable release requires X.Y.Z version format, got: $VERSION"
    exit 1
  fi

elif echo "$BRANCH" | grep -qE '^release/v[0-9]+\.[0-9]+\.[0-9]+$'; then
  if [ "$RELEASE_TYPE" != "rc" ]; then
    echo "Error: Release branch requires rc release type, got: $RELEASE_TYPE"
    exit 1
  fi

  if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+-rc\.[0-9]+$'; then
    echo "Error: RC release requires X.Y.Z-rc.N version format, got: $VERSION"
    exit 1
  fi
  BASE_VERSION="${VERSION%-rc*}"
  BRANCH_VERSION="${BRANCH#release/v}"
  if [ "$BASE_VERSION" != "$BRANCH_VERSION" ]; then
    echo "Error: Version base $BASE_VERSION does not match branch version $BRANCH_VERSION"
    exit 1
  fi

elif [ "$BRANCH" = "develop" ]; then
  if [ "$RELEASE_TYPE" != "dev" ]; then
    echo "Error: Develop branch requires dev release type, got: $RELEASE_TYPE"
    exit 1
  fi
  if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+-dev\.[0-9]+$'; then
    echo "Error: Dev release requires X.Y.Z-dev.N version format, got: $VERSION"
    exit 1
  fi

else
  echo "Error: Releases can only be triggered from develop, release/vX.Y.Z, or main"
  echo "Current branch: $BRANCH"
  exit 1
fi

echo "VERSION=$VERSION"
echo "TAG_NAME=$TAG_NAME"
echo "RELEASE_TYPE=$RELEASE_TYPE"
echo "RELEASE_BRANCH=$BRANCH"
echo "TEST_RELEASE=$TEST_RELEASE"
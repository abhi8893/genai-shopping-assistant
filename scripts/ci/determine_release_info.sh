#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-}"
REPO_ROOT="${2:-}"

if [ -z "$BRANCH" ]; then
  echo "Error: branch name argument is required" >&2
  exit 1
fi

if [ -z "$REPO_ROOT" ]; then
  echo "Error: repo root argument is required" >&2
  exit 1
fi

VERSION=$(python3 scripts/ci/get_version.py --repo-root "$REPO_ROOT")

if [ "$BRANCH" = "main" ]; then
  RELEASE_TYPE="stable"
  if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Stable release requires X.Y.Z version format, got: $VERSION"
    exit 1
  fi

elif echo "$BRANCH" | grep -qE '^release/v[0-9]+\.[0-9]+\.[0-9]+$'; then
  RELEASE_TYPE="rc"
  if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+-rc[0-9]+$'; then
    echo "Error: RC release requires X.Y.Z-rcN version format, got: $VERSION"
    exit 1
  fi
  BASE_VERSION="${VERSION%-rc*}"
  BRANCH_VERSION="${BRANCH#release/v}"
  if [ "$BASE_VERSION" != "$BRANCH_VERSION" ]; then
    echo "Error: Version base $BASE_VERSION does not match branch version $BRANCH_VERSION"
    exit 1
  fi

elif [ "$BRANCH" = "develop" ]; then
  RELEASE_TYPE="dev"
  if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+-dev[0-9]+$'; then
    echo "Error: Dev release requires X.Y.Z-devN version format, got: $VERSION"
    exit 1
  fi

else
  echo "Error: Releases can only be triggered from develop, release/vX.Y.Z, or main"
  echo "Current branch: $BRANCH"
  exit 1
fi

TAG_NAME="v${VERSION}"

echo "VERSION=$VERSION"
echo "TAG_NAME=$TAG_NAME"
echo "RELEASE_TYPE=$RELEASE_TYPE"

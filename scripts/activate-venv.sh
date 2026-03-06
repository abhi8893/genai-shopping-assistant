#!/bin/bash
# Activate a monorepo venv in current shell
# Usage: source ./scripts/activate-venv.sh <component> <target>
#
# Examples:
#   source ./scripts/activate-venv.sh packages/shopping-assistant dev
#   source ./scripts/activate-venv.sh services/ecom-backend prod
#   source ./scripts/activate-venv.sh root dev

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: source ./scripts/activate-venv.sh <component> <target>"
    echo ""
    echo "Examples:"
    echo "  source ./scripts/activate-venv.sh packages/shopping-assistant dev"
    echo "  source ./scripts/activate-venv.sh services/ecom-backend prod"
    echo "  source ./scripts/activate-venv.sh root dev"
    return 1
fi

COMPONENT="$1"
TARGET="$2"

# Get repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Determine component path
if [ "$COMPONENT" = "root" ]; then
    COMPONENT_PATH="$REPO_ROOT"
else
    COMPONENT_PATH="$REPO_ROOT/$COMPONENT"
fi

if [ ! -d "$COMPONENT_PATH" ]; then
    echo "Error: Component path does not exist: $COMPONENT_PATH"
    return 1
fi

# Normalize target name
if [[ ! "$TARGET" =~ ^\.venv- ]]; then
    TARGET=".venv-$TARGET"
fi

# Check for .venv (active) first, then .venv-{target}
ACTIVATE_PATH=""
if [ -d "$COMPONENT_PATH/.venv" ]; then
    # .venv exists - check if it's the target via .info.json
    if [ -f "$COMPONENT_PATH/.info.json" ]; then
        ACTIVE=$(grep -o '"active"[[:space:]]*:[[:space:]]*"[^"]*' "$COMPONENT_PATH/.info.json" | cut -d'"' -f4)
        if [ "$ACTIVE" = "$TARGET" ]; then
            ACTIVATE_PATH="$COMPONENT_PATH/.venv/bin/activate"
        fi
    fi
fi

# If not found as active, check for .venv-{target}
if [ -z "$ACTIVATE_PATH" ]; then
    if [ -d "$COMPONENT_PATH/$TARGET" ]; then
        ACTIVATE_PATH="$COMPONENT_PATH/$TARGET/bin/activate"
    fi
fi

if [ -z "$ACTIVATE_PATH" ] || [ ! -f "$ACTIVATE_PATH" ]; then
    echo "Error: Could not find activation script for $COMPONENT/$TARGET"
    echo "Available venvs in $COMPONENT:"
    ls -d "$COMPONENT_PATH"/.venv* 2>/dev/null | xargs -I {} basename {} || echo "  (none found)"
    return 1
fi

# Activate in current shell
. "$ACTIVATE_PATH"

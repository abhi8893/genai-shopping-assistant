## Virtual Environment Management

The monorepo uses a standardized virtual environment management system with Make targets. All components use `pyproject.toml` with PEP 735 dependency groups.

### Key Concepts

**Dependency Groups**:
- `dev`: Development dependencies (includes test group), uses **editable installs** (`-e`)
- `prod`: Production dependencies only, uses **non-editable installs**
- Custom groups (e.g., `test`): Non-editable installs

**Virtual Environment Naming**:
- `.venv-dev`: Development virtual environment
- `.venv-prod`: Production virtual environment
- `.venv-{group}`: Custom group virtual environment
- `.venv`: Active/current virtual environment (renamed from `.venv-{id}`)

**Component Identification**:
Components are identified by path in make targets:
- `root` - Special identifier for the repository root directory itself
- `packages/shopping-assistant` - Components under packages/
- `services/ecom-backend` - Components under services/

**State Tracking (`.info.json`)**:
Each component has a `.info.json` file with `venv` key that tracks:
- `options`: Array of ALL available venvs (union of physical `.venv-*` directories + active venv)
- `active`: Currently active venv name (what `.venv` represents), or `null` if none active
- Located at component root: `/.info.json` (for root), `packages/shopping-assistant/.info.json`, etc.

### Creating Virtual Environments

**Create venv for a single component**:
```bash
# Create root dev venv (editable install)
make venv-create COMPONENT=root GROUP=dev

# Create dev venv (editable install)
make venv-create COMPONENT=packages/shopping-assistant GROUP=dev

# Create prod venv (non-editable install)
make venv-create COMPONENT=services/ecom-backend GROUP=prod

# Create custom group venv
make venv-create COMPONENT=services/shopping-assistant GROUP=test
```

**Special: Root project venvs**:
The special component identifier `"root"` refers to the repository root itself:
- Maps to the root `/pyproject.toml` and root directory
- Useful for monorepo-level tools (pre-commit, documentation generators, etc.)
- Venvs created at repository root: `.venv-dev/`, `.venv-prod/`, etc.
- State tracked in `/.info.json`

**Create venvs for all components at once**:
```bash
# Create dev venvs for all components (including root)
make venv-create-all GROUP=dev

# Create prod venvs for all components (including root)
make venv-create-all GROUP=prod
```

**Note**: `venv-create-all` processes all components in order: `root` first, then packages and services. Root is always the first component in the list.

**What happens during creation**:
1. Creates `.venv-{group}` directory using `uv venv --python 3.12`
2. Installs dependencies based on group (editable for dev, non-editable otherwise)
3. For dev mode: reinstalls path-based dependencies (from `tool.uv.sources`) in editable mode
4. Updates `.info.json` with new venv in `options` array

### Cleaning Virtual Environments

**Clean specific venv**:
```bash
# Clean only dev venv
make venv-clean COMPONENT=packages/shopping-assistant GROUP=dev

# Clean only prod venv
make venv-clean COMPONENT=services/ecom-backend GROUP=prod
```

**Clean all venvs in a component**:
```bash
# Removes all .venv* directories (including .venv if present)
make venv-clean COMPONENT=packages/shopping-assistant
```

**Clean all components**:
```bash
# Clean all venvs in all components
make venv-clean-all

# Clean specific group across all components
make venv-clean-all GROUP=dev
```

**What happens during cleaning**:
- If `GROUP` specified: removes only `.venv-{group}`, updates `.info.json` options
- If `GROUP` not specified: removes all `.venv*` directories, clears `.info.json` to empty state

**Enhanced: Cleaning active venvs**:
Since v0.x+, `venv-clean` recognizes when a venv is currently active (renamed to `.venv`) and operates on it:
```bash
# This now works even if .venv-dev is currently active (at .venv)
make venv-clean COMPONENT=root GROUP=dev
```
The script checks `.info.json` to find the active venv and cleans it properly, then sets `active: null`.

### Switching Virtual Environments

**Switch to a different venv**:
```bash
# Switch to dev venv
make venv-switch COMPONENT=services/shopping-assistant TARGET=dev

# Switch to prod venv
make venv-switch COMPONENT=packages/shopping-assistant TARGET=prod
```

**How switching works**:
1. If venv already active: deactivates by renaming `.venv` → `.venv-{old}`
2. Activates target: renames `.venv-{target}` → `.venv`
3. Repairs stale `VIRTUAL_ENV` path references in `bin/` activate scripts (see below)
4. Updates `.info.json` with `active: ".venv-{target}"`
5. Updates `options` to include both physical `.venv-*` dirs and active venv

**Important**: Target venv must exist before switching (create with `venv-create` first)

### Unswitching Virtual Environments

**Unswitch a specific component** (reverse a `venv-switch`):
```bash
# Reverse the switch - renames .venv back to .venv-{active}
make venv-unswitch COMPONENT=packages/shopping-assistant
```

**Unswitch all components at once**:
```bash
# Reverse all switches across all components
make venv-unswitch-all
```

**How unswitching works**:
1. Reads `.info.json` to find the currently active venv name
2. Renames `.venv` back to `.venv-{active}` (original name)
3. Sets `active: null` in `.info.json`
4. Updates `options` array to reflect current physical directories

**When to use unswitch**:
- You used `venv-switch` and want to revert to independent `.venv-{group}` directories
- Workflow: `venv-switch` → work → `venv-unswitch`

### Activating Venvs in Current Shell

**Activate a venv session-level** (in current terminal only):
```bash
# Activate venv for current terminal session
source scripts/activate-venv.sh packages/shopping-assistant dev
source scripts/activate-venv.sh services/ecom-backend prod
source scripts/activate-venv.sh root dev
```

**How activation works**:
1. Script finds the component path
2. Checks if venv is active (`.venv`) or inactive (`.venv-{group}`) via `.info.json`
3. Sources the activation script directly in current shell using `.` operator
4. `VIRTUAL_ENV` is set in your current terminal (not a subshell)

**Deactivate**:
```bash
# Standard Python venv deactivation
deactivate
```

**Key differences from `venv-switch`**:

| Feature | venv-switch | activate-venv.sh |
|---------|----------|---------|
| Scope | Filesystem-wide | Current shell only |
| Persistence | Persists across shells | Only this terminal |
| Cleanup | Revert with `venv-unswitch` | Just run `deactivate` |
| Use case | Long-term development | Quick testing/switching |

### Repairing VIRTUAL_ENV References

When a venv is renamed (e.g. `.venv-dev` → `.venv`), the activate scripts inside `bin/`
still contain hardcoded paths to the old directory name. `venv-switch` repairs these
automatically, but the targets below allow ad-hoc repairs if needed.

**Repair active `.venv` for a single component**:
```bash
make venv-repair-refs COMPONENT=packages/shopping-assistant
```

**Repair a specific non-active venv**:
```bash
make venv-repair-refs COMPONENT=packages/shopping-assistant TARGET=dev
```

**Repair all components** (optional `TARGET` works here too):
```bash
make venv-repair-refs-all
make venv-repair-refs-all TARGET=prod
```

**Dry-run to inspect without writing**:
```bash
python3 scripts/repair_venv_references.py \
  --venv-dir packages/shopping-assistant [--target dev] --dry-run
```

The underlying script is `scripts/repair_venv_references.py` and is also importable
as a module (`from repair_venv_references import repair_venv_references`).

### Refreshing .info.json

**Refresh and validate .info.json**:
```bash
# Refresh single component
make venv-refresh COMPONENT=packages/shopping-assistant

# Auto-fix invalid active field
make venv-refresh COMPONENT=packages/shopping-assistant FIX_ACTIVE=true

# Refresh all components
make venv-refresh-all
```

**Validation rules**:
1. `active` must not be `.venv` (should be `.venv-{id}` format)
2. If `active` is `.venv-{id}`, then `.venv-{id}` directory must NOT exist (should have been renamed to `.venv`)
3. If `active` is set, `.venv` directory must exist

### Understanding .info.json

**Example valid state** (after switching to prod):
```json
{
    "venv": {
        "options": [".venv-dev", ".venv-prod"],
        "active": ".venv-prod"
    }
}
```
- Physical directories: `.venv-dev/`, `.venv/`
- `.venv/` represents the activated `.venv-prod`
- `options` includes both `.venv-dev` (physical) and `.venv-prod` (active as `.venv`)

**Example valid state** (no active venv):
```json
{
    "venv": {
        "options": [".venv-dev", ".venv-prod"],
        "active": null
    }
}
```
- Physical directories: `.venv-dev/`, `.venv-prod/`
- No venv currently activated
- Both options are physical directories

### Internal Package Dependencies

Services that depend on internal packages use `tool.uv.sources`:

```toml
[project]
dependencies = ["shopping-assistant", "python-dotenv"]

[tool.uv.sources]
shopping-assistant = { path = "../../packages/shopping-assistant" }
```

**Dev mode handling**:
- Path dependencies are installed normally with other deps
- Then reinstalled in editable mode (`-e`) in a second pass
- This ensures dev workflow has editable internal packages

### Python Version Pinning

`.python-version` files are managed via `uv python pin` and exist at the repo root and in each component directory. `PYTHON_VERSION` defaults to `3.12` (matching `.github/workflows/main.yml`).

```bash
# Pin repo root (no COMPONENT)
make venv-pin-python

# Pin a single component
make venv-pin-python COMPONENT=packages/shopping-assistant

# Pin root + all components
make venv-pin-python-all

# Override Python version
make venv-pin-python-all PYTHON_VERSION=3.13
```

### Root Project Venv

The repository root has its own `pyproject.toml` with root-level dependencies:

```toml
[dependency-groups]
dev = [
    "pre-commit"
]
```

**Create and use root dev venv**:
```bash
# Create root dev venv with pre-commit and dependencies
make venv-create COMPONENT=root GROUP=dev

# Switch to root dev venv
make venv-switch COMPONENT=root TARGET=dev

# Activate the root venv
source .venv/bin/activate

# Verify pre-commit is available
pre-commit --version
```

**Root venv use cases**:
- Install monorepo-level tools (pre-commit, documentation generators)
- Run root-level scripts and utilities
- Create isolated root environment for container builds
- Pin development tools independent of component venvs

### Common Venv Workflows

**Setting up a new development environment**:
```bash
# Create dev venvs for all components (including root)
make venv-create-all GROUP=dev

# Activate the root venv (for pre-commit and monorepo tools)
make venv-switch COMPONENT=root TARGET=dev
source .venv/bin/activate

# Then activate the venv for the component you're working on
source packages/shopping-assistant/.venv/bin/activate

# Verify all .info.json files are valid
make venv-refresh-all
```

**Switching between dev and prod mode**:
```bash
# Create both venvs
make venv-create COMPONENT=services/shopping-assistant GROUP=dev
make venv-create COMPONENT=services/shopping-assistant GROUP=prod

# Switch to dev for development
make venv-switch COMPONENT=services/shopping-assistant TARGET=dev
source services/shopping-assistant/.venv/bin/activate

# Switch to prod to test production behavior
make venv-switch COMPONENT=services/shopping-assistant TARGET=prod
source services/shopping-assistant/.venv/bin/activate
```

**Cleaning up and starting fresh**:
```bash
# Remove all venvs everywhere
make venv-clean-all

# Recreate dev venvs
make venv-create-all GROUP=dev
```

**Using venv-unswitch** (reverse a persistent switch):
```bash
# Create and switch to dev
make venv-create COMPONENT=packages/shopping-assistant GROUP=dev
make venv-switch COMPONENT=packages/shopping-assistant TARGET=dev

# Work in the switched state...

# Reverse the switch when done
make venv-unswitch COMPONENT=packages/shopping-assistant

# Verify: should show .venv-dev as physical directory, active=null
cat packages/shopping-assistant/.info.json
```

**Using activate-venv.sh** (session-level activation):
```bash
# Activate for current terminal only
source scripts/activate-venv.sh packages/shopping-assistant dev

# Verify activation
echo $VIRTUAL_ENV

# Do work in current shell...

# Deactivate when done
deactivate

# Note: .venv-dev still exists as separate directory, unchanged
```

**Cleaning active venvs without unswitching first**:
```bash
# Old way (required unswitching first):
make venv-switch COMPONENT=root TARGET=dev
make venv-unswitch COMPONENT=root
make venv-clean COMPONENT=root GROUP=dev

# New way (works directly):
make venv-switch COMPONENT=root TARGET=dev
make venv-clean COMPONENT=root GROUP=dev  # ✅ Works! Detects .venv as active .venv-dev
```
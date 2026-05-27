## Virtual Environment Management

The monorepo uses a standardized virtual environment management system via the `project` CLI (located at `packages/project`). All components use `pyproject.toml` with PEP 735 dependency groups.

### Quick Start: Activate the Project CLI

The `project` CLI commands are the primary interface for venv management. Initialize it once per session:

```bash
# Bootstrap the CLI into the root .venv (one-time per session)
make setup-project-cli

# Activate the CLI in your current shell
source .venv/bin/activate

# Verify the CLI is available
project venv show
```

After activation, use `project venv *` commands directly. The old `make venv-*` targets are deprecated and should not be used.

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
project venv create root --group dev

# Create dev venv (editable install)
project venv create packages/shopping-assistant --group dev

# Create prod venv (non-editable install)
project venv create services/ecom-backend --group prod

# Create custom group venv
project venv create services/shopping-assistant --group test
```

**Flags for venv creation**:
- `--missing-only`: Skip components that already have the venv (useful for batch creation)
- `--overwrite`: Remove existing venv and recreate it (forces clean install)

**Special: Root project venvs**:
The special component identifier `"root"` refers to the repository root itself:
- Maps to the root `/pyproject.toml` and root directory
- Useful for monorepo-level tools (pre-commit, documentation generators, etc.)
- Venvs created at repository root: `.venv-dev/`, `.venv-prod/`, etc.
- State tracked in `/.info.json`

**Create venvs for all components at once**:
```bash
# Create dev venvs for all components (including root)
project venv create --all --group dev

# Create prod venvs for all components (including root)
project venv create --all --group prod
```

**Note**: When using `--all`, components are processed in order: `root` first, then packages and services. Root is always the first component in the list.

**What happens during creation**:
1. Creates `.venv-{group}` directory using `uv venv --python 3.12`
2. Installs dependencies based on group (editable for dev, non-editable otherwise)
3. For dev mode: reinstalls path-based dependencies (from `tool.uv.sources`) in editable mode
4. Updates `.info.json` with new venv in `options` array
5. Includes self-healing automation to prevent active `.venv-*` duplications when using `--overwrite`

### Cleaning Virtual Environments

**Clean specific venv**:
```bash
# Clean only dev venv
project venv clean packages/shopping-assistant --group dev

# Clean only prod venv
project venv clean services/ecom-backend --group prod
```

**Clean all venvs in a component**:
```bash
# Removes all .venv* directories (including .venv if present)
project venv clean packages/shopping-assistant
```

**Clean all components**:
```bash
# Clean all venvs in all components
project venv clean --all

# Clean specific group across all components
project venv clean --all --group dev
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
project venv switch services/shopping-assistant --target dev

# Switch to prod venv
project venv switch packages/shopping-assistant --target prod
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
project venv unswitch packages/shopping-assistant
```

**Unswitch all components at once**:
```bash
# Reverse all switches across all components
project venv unswitch --all
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
still contain hardcoded paths to the old directory name. `project venv switch` repairs these
automatically, but the command below allows ad-hoc repairs if needed.

**Repair active `.venv` for a single component**:
```bash
project venv repair-refs packages/shopping-assistant
```

**Repair a specific non-active venv**:
```bash
project venv repair-refs packages/shopping-assistant --target dev
```

**Repair all components** (optional `--target` works here too):
```bash
project venv repair-refs --all
project venv repair-refs --all --target prod
```

The `repair-refs` command updates `VIRTUAL_ENV=` paths in activation scripts to match current directory names.

### Refreshing .info.json

**Refresh and validate .info.json**:
```bash
# Refresh single component
project venv refresh packages/shopping-assistant

# Auto-fix invalid active field
project venv refresh packages/shopping-assistant --fix

# Refresh all components
project venv refresh --all
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

`.python-version` files are managed via `uv python pin` and exist at the repo root and in each component directory. The default is `3.12` (matching `.github/workflows/main.yml`).

Currently, Python version pinning is managed directly with `uv`:

```bash
# Pin Python version at repo root
uv python pin 3.12

# Pin Python version in a component
cd packages/shopping-assistant && uv python pin 3.12
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
project venv create root --group dev

# Switch to root dev venv
project venv switch root --target dev

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
- Bootstrap the `project` CLI itself via `make setup-project-cli`

### Common Venv Workflows

**Setting up a new development environment**:
```bash
# Bootstrap the project CLI (one-time)
make setup-project-cli
source .venv/bin/activate

# Create dev venvs for all components (including root)
project venv create --all --group dev

# Activate the root venv (for pre-commit and monorepo tools)
project venv switch root --target dev
source .venv/bin/activate

# Then activate the venv for the component you're working on
source packages/shopping-assistant/.venv/bin/activate

# Verify all .info.json files are valid
project venv refresh --all
```

**Switching between dev and prod mode**:
```bash
# Create both venvs
project venv create services/shopping-assistant --group dev
project venv create services/shopping-assistant --group prod

# Switch to dev for development
project venv switch services/shopping-assistant --target dev
source services/shopping-assistant/.venv/bin/activate

# Switch to prod to test production behavior
project venv switch services/shopping-assistant --target prod
source services/shopping-assistant/.venv/bin/activate
```

**Cleaning up and starting fresh**:
```bash
# Remove all venvs everywhere
project venv clean --all

# Recreate dev venvs
project venv create --all --group dev
```

**Using venv-unswitch** (reverse a persistent switch):
```bash
# Create and switch to dev
project venv create packages/shopping-assistant --group dev
project venv switch packages/shopping-assistant --target dev

# Work in the switched state...

# Reverse the switch when done
project venv unswitch packages/shopping-assistant

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
# The project CLI handles active venvs automatically:
project venv switch root --target dev
project venv clean root --group dev  # ✅ Works! Detects .venv as active .venv-dev and cleans it

# Or equivalently:
project venv switch root --target dev
project venv clean root  # Cleans all venvs including active
```

The CLI automatically detects active venvs via `.info.json` and operates on them correctly.
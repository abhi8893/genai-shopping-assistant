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

**State Tracking (`.info.json`)**:
Each component has a `.info.json` file with `venv` key that tracks:
- `options`: Array of ALL available venvs (union of physical `.venv-*` directories + active venv)
- `active`: Currently active venv name (what `.venv` represents), or `null` if none active

### Creating Virtual Environments

**Create venv for a single component**:
```bash
# Create dev venv (editable install)
make venv-create COMPONENT=packages/shopping-assistant GROUP=dev

# Create prod venv (non-editable install)
make venv-create COMPONENT=services/ecom-backend GROUP=prod

# Create custom group venv
make venv-create COMPONENT=services/shopping-assistant GROUP=test
```

**Create venvs for all components at once**:
```bash
# Create dev venvs for all components
make venv-create-all GROUP=dev

# Create prod venvs for all components
make venv-create-all GROUP=prod
```

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
3. Updates `.info.json` with `active: ".venv-{target}"`
4. Updates `options` to include both physical `.venv-*` dirs and active venv

**Important**: Target venv must exist before switching (create with `venv-create` first)

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

### Common Venv Workflows

**Setting up a new development environment**:
```bash
# Create dev venvs for all components
make venv-create-all GROUP=dev

# Activate the venv for the component you're working on
source packages/shopping-assistant/.venv-dev/bin/activate

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
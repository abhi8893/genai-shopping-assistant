# direnv Auto-activation Setup

This document describes how direnv is configured to auto-activate Python virtual environments when `cd`-ing into project directories, with descriptive prompt names.

## Prompt Format

| Directory | Active venv | Prompt shows |
|---|---|---|
| repo root | `.venv` | `(root)` |
| `packages/shopping-assistant` | `.venv-dev` active | `(packages/shopping-assistant@dev)` |
| `services/ecom-backend` | `.venv-prod` active | `(services/ecom-backend@prod)` |
| any | no `.venv` | reminder message |

## One-time Machine Setup

### 1. Install direnv
```bash
brew install direnv
```

### 2. Add to `~/.zshrc` (after `source $ZSH/oh-my-zsh.sh`)
```zsh
# Show active virtual environment in prompt (reads VIRTUAL_ENV_PROMPT set by direnv)
function _venv_prompt_info() {
  [[ -n "$VIRTUAL_ENV_PROMPT" ]] && echo -n "($VIRTUAL_ENV_PROMPT) "
}
PROMPT='$(_venv_prompt_info)'"$PROMPT"
```

### 3. Add direnv hook to `~/.zshrc` (end of file)
```zsh
eval "$(direnv hook zsh)"
```

### 4. Reload shell
```bash
source ~/.zshrc
```

## Per-clone Project Setup

### 5. Generate and allow `.envrc` files
```bash
make direnv-setup
```

This creates `.envrc` in the repo root and each component directory, and runs `direnv allow` for each.

### 6. Create venvs (prompt name is now baked in via `--prompt`)
```bash
make venv-create-all GROUP=dev
```

### 7. Activate a venv
```bash
make venv-switch COMPONENT=packages/shopping-assistant TARGET=dev
```

After switching, `cd`-ing into the directory auto-activates the venv and updates the prompt.

## Day-to-day Usage

```bash
cd packages/shopping-assistant
# direnv: loading .envrc
# prompt → (packages/shopping-assistant@dev) ➜ ...

cd services/ecom-backend
# direnv: loading .envrc
# prompt → (services/ecom-backend@dev) ➜ ...

cd ~
# prompt → ➜ ...   (venv deactivated automatically)
```

If you see `direnv: no .venv found, run: make venv-create ...`:
```bash
make venv-create COMPONENT=<component> GROUP=dev
make venv-switch COMPONENT=<component> TARGET=dev
```

If `.envrc` files are regenerated (`make direnv-setup`), direnv will prompt you to re-allow them — just run `make direnv-setup` again to re-allow automatically.

## How It Works

1. `make direnv-setup` writes `.envrc` to root + all components and runs `direnv allow` (using `cwd=` not a path arg)
2. Each `.envrc` sets `VIRTUAL_ENV_DISABLE_PROMPT=1` before sourcing `.venv/bin/activate` — this prevents the activate script from modifying `PS1` directly (which would cause double prompt display)
3. direnv exports `VIRTUAL_ENV_PROMPT` to the shell
4. `_venv_prompt_info` in `~/.zshrc` reads `VIRTUAL_ENV_PROMPT` and prepends it to `$PROMPT` using `PROMPT_SUBST`

The prompt name itself is baked into the venv at creation time via `uv venv --prompt {component}@{group}`, which sets it in `pyvenv.cfg` and all activate scripts.

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
VENV_PATH="${REPO_ROOT}/.venv"
PYTHON_BIN="${PYTHON:-python3}"

log() {
  local level="$1"
  shift
  printf '[%s] %s\n' "$level" "$*"
}

fail() {
  log "ERROR" "$*" >&2
  exit 1
}

ensure_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    fail "Required command '$cmd' not found in PATH. Run 'make bootstrap' or install it manually."
  fi
}

ensure_venv() {
  if [ ! -d "$VENV_PATH" ]; then
    log INFO "Creating Python virtual environment at $VENV_PATH"
    ensure_command "$PYTHON_BIN"
    "$PYTHON_BIN" -m venv "$VENV_PATH"
  fi
}

with_venv() {
  ensure_venv
  # shellcheck disable=SC1090
  source "$VENV_PATH/bin/activate"
}

pip_install() {
  with_venv
  pip install --upgrade pip
  pip install --upgrade "$@"
}

run_python() {
  with_venv
  python "$@"
}

ensure_node_modules() {
  local node_dir="$1"
  if [ -f "$node_dir/package.json" ]; then
    log INFO "Installing Node dependencies in $node_dir"
    (cd "$node_dir" && npm install)
  fi
}


#!/usr/bin/env bash
# Install the Agora RoundTable opencode plugin bundle into the global opencode config.
#
#   bash opencode-plugin/install.sh [config-dir]
#
# - config-dir defaults to $HOME/.config/opencode
# - Symlinks this bundle's commands/, agents/, skills/, and plugin/ into the config so
#   a checkout stays the single source of truth (no drift).
# - Optionally symlinks the personas data dir to the Claude plugin's dir for sharing
#   (only if ~/.claude/agora-roundtable exists; skipped otherwise so non-Claude users
#   are unaffected).
#
# Works in-place from the repo. Safe to re-run (idempotent).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${1:-$HOME/.config/opencode}"

BUNDLE_DIR="$SCRIPT_DIR"

mkdir -p "$CONFIG_DIR"

link() {
  # $1 = subdir name (commands|agents|skills)
  # $2 = destination subdir (may differ, e.g. plugin -> plugins)
  local sub="$1"
  local dstsub="${2:-$1}"
  local src="$BUNDLE_DIR/$sub"
  local dst="$CONFIG_DIR/$dstsub"
  if [ ! -d "$src" ]; then
    echo "  skip $sub (nothing in $src)"
    return
  fi
  mkdir -p "$dst"
  for item in "$src"/*; do
    [ -e "$item" ] || continue
    local name; name="$(basename "$item")"
    local target="$dst/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "  WARN $target exists and is not a symlink — leaving as-is"
      continue
    fi
    ln -sfn "$item" "$target"
    echo "  linked $target -> $item"
  done
}

echo "Installing Agora RoundTable into $CONFIG_DIR"

# Ensure the JS plugin's own dependency (@opencode-ai/plugin) is available next to the
# file so module resolution works when opencode loads the symlinked plugin.
if [ -f "$BUNDLE_DIR/package.json" ] && command -v bun >/dev/null 2>&1; then
  if [ ! -d "$BUNDLE_DIR/node_modules/@opencode-ai/plugin" ]; then
    echo "  installing plugin deps with bun..."
    (cd "$BUNDLE_DIR" && bun install >/dev/null 2>&1) || true
  else
    echo "  plugin deps already present"
  fi
fi

link commands
link agents
link skills
link plugin plugins

# The JS plugin needs @opencode-ai/plugin available at runtime; declare it so opencode
# runs bun install in the config dir. Preserve any existing package.json deps.
if [ ! -f "$CONFIG_DIR/package.json" ]; then
  cat > "$CONFIG_DIR/package.json" <<'JSON'
{
  "dependencies": {
    "@opencode-ai/plugin": "^1.18.0"
  }
}
JSON
  echo "  wrote $CONFIG_DIR/package.json (plugin dependency)"
fi

# Persona data dir — share with Claude if it exists, else opencode-native.
PERSONAS_SRC="$HOME/.claude/agora-roundtable/personas"
AGORA_DIR="$CONFIG_DIR/agora"
if [ -d "$PERSONAS_SRC" ]; then
  mkdir -p "$AGORA_DIR"
  if [ -e "$AGORA_DIR/personas" ] && [ ! -L "$AGORA_DIR/personas" ]; then
    echo "  WARN $AGORA_DIR/personas exists and is not a symlink — leaving as-is"
  else
    ln -sfn "$PERSONAS_SRC" "$AGORA_DIR/personas"
    echo "  linked personas -> $PERSONAS_SRC (Claude share)"
  fi
else
  mkdir -p "$AGORA_DIR/personas"
  echo "  personas dir: $AGORA_DIR/personas (opencode-native; no Claude detected)"
fi

echo "Done. Commands are available after restarting opencode as /agora*."

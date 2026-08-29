import { homedir } from "node:os"
import { join } from "node:path"
import { existsSync } from "node:fs"

// Resolve where Agora personas live, opencode-native with an optional
// Claude-share fallback. Never REQUIRES Claude to exist.
//
// Resolution order:
//   1. $AGORA_DATA_DIR                      — explicit override (env)
//   2. $CLAUDE_PLUGIN_DATA/agora-roundtable — the real Claude plugin data dir
//      (the authoritative place built personas live; only if it exists)
//   3. ~/.config/opencode/agora            — opencode-native default
//   4. ~/.claude/agora-roundtable          — legacy Claude fallback (only if it exists)
//
// The "personas" subfolder holds one folder per person (a slug folder with
// persona.md, research/, transcripts/, inbox/). Session/preset state lives
// alongside it.
export function personaRoot() {
  if (process.env.AGORA_DATA_DIR) {
    return process.env.AGORA_DATA_DIR
  }
  // Prefer the real Claude plugin data dir when present, so opencode reuses
  // the same personas Claude Code built (and vice versa).
  const pluginData = process.env.CLAUDE_PLUGIN_DATA
    ? join(process.env.CLAUDE_PLUGIN_DATA, "agora-roundtable")
    : ""
  if (pluginData && existsSync(join(pluginData, "personas"))) {
    return pluginData
  }
  const base = process.env.OPENCODE_CONFIG
    ? join(process.env.OPENCODE_CONFIG, "agora")
    : join(homedir(), ".config", "opencode", "agora")
  return base
}

// Full personas directory (the canonical location for this root).
export function personasDir() {
  return join(personaRoot(), "personas")
}

// The active shared personas path, with fallbacks for machines where the
// opencode-native or Claude-share dirs exist but the resolved root didn't match.
export function resolvePersonasDir() {
  const native = personasDir()
  if (existsSync(native)) return native
  const pluginData = process.env.CLAUDE_PLUGIN_DATA
    ? join(process.env.CLAUDE_PLUGIN_DATA, "agora-roundtable", "personas")
    : ""
  if (pluginData && existsSync(pluginData)) return pluginData
  const legacy = join(homedir(), ".claude", "agora-roundtable", "personas")
  if (existsSync(legacy)) return legacy
  return native
}

export function slugify(name) {
  return name
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
}

export function personaDir(slug) {
  return join(resolvePersonasDir(), slug)
}

export function roundtablePresetsFile() {
  return join(resolvePersonasDir(), "roundtable-presets.json")
}

export function roundtableSessionFile() {
  return join(resolvePersonasDir(), "roundtable-session.json")
}

import { homedir } from "node:os"
import { join } from "node:path"
import { existsSync } from "node:fs"

// Resolve where Agora personas live. The location is deliberately agent-neutral:
// it belongs to no single tool (not opencode, Claude, or codex), so every agent
// that runs the Agora port reads and writes the same people.
//
// Resolution order:
//   1. $AGORA_DATA_DIR — explicit override (env), e.g. a synced or custom location
//   2. ~/.agora        — the neutral default, identical on Linux, macOS, and Windows
//
// The "personas" subfolder holds one folder per person (a slug folder with
// persona.md, research/, transcripts/, inbox/). Session/preset state lives
// alongside it.
export function personaRoot() {
  if (process.env.AGORA_DATA_DIR) {
    return process.env.AGORA_DATA_DIR
  }
  return join(homedir(), ".agora")
}

// Full personas directory (the canonical location for this root).
export function personasDir() {
  return join(personaRoot(), "personas")
}

// The active shared personas path, with a one-time bridge to data written by
// older installs (which kept personas under the opencode config dir).
export function resolvePersonasDir() {
  const native = personasDir()
  if (existsSync(native)) return native
  const legacy = join(homedir(), ".config", "opencode", "agora", "personas")
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

# Agora RoundTable for OpenCode

The opencode-native port of [Agora RoundTable](../README.md) — turn any public figure
into a personal coach, run multi-coach roundtables, and run real multi-round **warm-agent
debates** between them.

It stores personas in an **agent-neutral** directory (`~/.agora`), so a persona is shared
across opencode, Claude, codex, and any other tool that runs the Agora port.

## Install

From inside this repo:

```bash
bash opencode-plugin/install.sh
```

This links the bundle into your global opencode config:

- `commands/` → 15 slash commands (`/agora …`)
- `agents/` → the facilitator + hidden coach subagents
- `skills/` → the person-building pipeline
- `plugins/plugin.js` → a tiny real **shim** that re-exports the JS plugin (the
  data-dir + session tools) from this checkout

The plugin's entry point is a shim rather than a symlink on purpose: opencode's plugin
loader cannot load a plugin whose entry file is a symlink pointing outside the config
dir, so the installer writes a one-line `export { default } from "file://…"` pointer
instead. The repo stays the single source of truth; the plugin has no runtime
dependencies.

Personas live in an agent-neutral `~/.agora/personas` (override with `$AGORA_DATA_DIR`), so
opencode, Claude, codex, and any other tool share one set of people. No Claude installation
is required, and no single tool's config dir owns the data.

opencode picks up the change automatically; **restart it** if the commands or plugin
don't appear.

> Uninstall: `rm -rf ~/.config/opencode/commands ~/.config/opencode/agents
> ~/.config/opencode/skills/agora-coach ~/.config/opencode/plugins/plugin.js`
> (the repo is untouched; the symlinks and the generated plugin shim are removed).
> Your personas in `~/.agora` are left alone.

## Commands

| Command | What it does |
|---|---|
| `/agora coach <name>` | Build or load a persona, talk one-on-one |
| `/agora coach-switch <name>` · `/agora coach-end` · `/agora coach-list` | Swap · exit · list already-built coaches |
| `/agora coach-refresh <name>` | Rebuild a persona from fresh research |
| `/agora coach-update <name>` | Sync files dropped in a coach's `inbox/` into research |
| `/agora coach-gaps [name]` | Audit where a coach's sourcing is thin |
| `/agora roundtable <names> or <preset>` | Open a multi-coach session |
| `/agora discuss <topic>` | Run a real multi-round debate between active coaches |
| `/agora roundtable-save <preset>` · add · remove · end | Manage the table |
| `/agora coach-refresh-all` · `/agora coach-update-all` | Same, across all coaches or a preset |

## How the warm-agent debate works

Each coach is a dedicated `agora-coach` subagent with its **own independent context**,
spawned once and resumed across rounds. That's what lets a coach say *"you've moved me"* —
it still holds the position it staked in round one. Rounds repeat until positions stop
moving (or 5 rounds cap), then a gap check asks each coach where its own sourcing was
thin and writes those gaps to `research/_gaps.md`.

## Portability

The plugin resolves the personas directory in this order:

1. `$AGORA_DATA_DIR/personas` — explicit env override (a synced or custom location)
2. `~/.agora/personas` — the neutral default

The location is agent-neutral on purpose: it belongs to no single tool, so opencode, Claude,
codex, and any other agent share the same people. `~/.agora` resolves identically on Linux,
macOS, and Windows (Node's `homedir()`), and nothing has to be installed to use it.

Older installs that kept personas under `~/.config/opencode/agora` are bridged automatically
(the plugin still reads that path if `~/.agora/personas` is missing), and `install.sh`
migrates the data across once.

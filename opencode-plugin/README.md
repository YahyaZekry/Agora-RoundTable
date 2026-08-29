# Agora RoundTable for OpenCode

The opencode-native port of [Agora RoundTable](../README.md) — turn any public figure
into a personal coach, run multi-coach roundtables, and run real multi-round **warm-agent
debates** between them.

It shares the **same persona format and data directory** as the Claude Code plugin, so a
persona you build with Claude's `/coach` is instantly usable here and vice versa.

## Install

From inside this repo:

```bash
bash opencode-plugin/install.sh
```

This symlinks the bundle into your global opencode config:

- `commands/` → 15 slash commands (`/agora …`)
- `agents/` → the facilitator + hidden coach subagents
- `skills/` → the person-building pipeline
- `plugin/plugins` → the JS plugin (data-dir + session tools)

It also links `~/.config/opencode/agora/personas` to `~/.claude/agora-roundtable/personas`
**if Claude's folder exists** (shared personas). If it doesn't, you get an opencode-native
`~/.config/opencode/agora/personas` instead — no Claude required.

**Restart opencode** after installing.

> Uninstall: `rm -rf ~/.config/opencode/commands ~/.config/opencode/agents
> ~/.config/opencode/skills/agora-coach ~/.config/opencode/plugins/plugin.js
> ~/.config/opencode/agora` (these are symlinks; the repo is untouched).

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

1. `$AGORA_DATA_DIR/personas` (env override)
2. `~/.config/opencode/agora/personas` (opencode-native)
3. `~/.claude/agora-roundtable/personas` — **only if it already exists** (Claude share)

So the opencode port never requires Claude to be installed, but reuses Claude personas when
present. A user who only runs opencode gets an isolated, self-contained setup.

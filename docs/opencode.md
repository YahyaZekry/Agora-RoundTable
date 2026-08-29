# Agora RoundTable — OpenCode port

Agora RoundTable is now available as a native **opencode** bundle in `opencode-plugin/`,
with full parity with the original Claude Code plugin (all 15 commands).

## Architecture (why this shape)

Claude Code registers slash commands dynamically from a JS plugin. opencode does **not** —
its commands, agents, and skills are config files. So the port is a hybrid:

| Piece | opencode mechanism |
|---|---|
| 15 commands (`/agora*`) | `commands/*.md` (frontmatter: `agent`, `subtask`) |
| Facilitator + hidden coach subagents | `agents/*.md` (`mode: subagent`, `hidden: true`) |
| Persona-building pipeline | `skills/agora-coach/SKILL.md` |
| Data-dir + session/preset state tools | a real JS **plugin** in `plugin/plugin.js` |

The JS plugin exists only where opencode needs runtime power: resolving the portable data
dir and persisting roundtable session/preset JSON. Everything else is declarative config.

## Install

```bash
bash opencode-plugin/install.sh          # the pack itself
cd opencode-plugin && bun install         # only for the JS plugin dep
```

Install symlinks the bundle into `~/.config/opencode` (commands → `commands/`, agents →
`agents/`, skill → `skills/agora-coach`, plugin → `plugins/`). The repo stays the single
source of truth; re-running is safe.

**Restart opencode** after installing.

## Personas data dir (portability)

Resolved in this order by `lib/data-dir.js` and the facilitator agent:

1. `$AGORA_DATA_DIR/personas`
2. `~/.config/opencode/agora/personas` (opencode-native)
3. `~/.claude/agora-roundtable/personas` — **only if it already exists**

The install script makes `~/.config/opencode/agora/personas` a **symlink to the Claude
dir when present**, so a persona built by Claude's `/coach` is immediately usable in
opencode and vice versa. On a machine with no Claude, you get a clean isolated dir — the
port never *requires* `~/.claude`.

## Commands

```
/agora coach <name>            build or load a persona, talk one-on-one
/agora coach-switch <name>     swap to another coach
/agora coach-end               exit coach mode
/agora coach-list              list already-built coaches
/agora coach-refresh <name>    rebuild a persona from fresh research
/agora coach-refresh-all       refresh every coach (or a preset)
/agora coach-update <name>     sync files dropped in a coach's inbox/ into research
/agora coach-update-all        update all coaches (or a preset)
/agora coach-gaps [name]       audit where a coach's sourcing is thin
/agora roundtable <list/name>  open a multi-coach session
/agora roundtable-save <name>  save the current table as a reusable preset
/agora roundtable-add <name>   add a coach to the table
/agora roundtable-remove <n>   remove a coach
/agora roundtable-end          close the session
/agora discuss <topic>         run a real multi-round warm-agent debate
```

## How /agora discuss works (warm agents)

Each coach is a dedicated `agora-coach` subagent with **its own independent context**,
spawned once and resumed across rounds via the `task` tool's `task_id`. That continuity is
what lets a coach say "you've moved me" — it still holds the position it staked in round 1.

- **Round 1 (cold, parallel):** spawn all coaches at once; each states a clear position.
- **Rounds 2..N (warm, parallel):** resume each subagent with the others' last statements.
- **Stop:** CONVERGED, CRYSTALLIZED (a full round where everyone reported `movedBy:none`
  and `newArgument:no` — still disagree, reported as a finished choice, not a failure), or
  CAPPED at 5 rounds.
- **Gap audit:** resume each coach once more out of character to find where its own
  sourcing was thin; gaps route to `research/_gaps.md`.

## Local file layout

```
opencode-plugin/
  install.sh              symlinks the bundle into ~/.config/opencode
  package.json            declares @opencode-ai/plugin (for plugin.js)
  commands/agora-*.md     15 slash commands
  agents/
    agora-facilitator.md  orchestrator (builds personas, runs debates)
    agora-coach.md        hidden single-coach subagent
  skills/agora-coach/     shared persona-building pipeline (SKILL.md + refs)
  plugin/plugin.js        JS plugin: agora_data_dir, agora_slugify, agora_session
  lib/data-dir.js         portable data-dir resolver + slugify
  README.md               quick reference
```

## Publish path (future)

Because the bundle is plain config files + a small ESM plugin with a package.json, it can
be distributed as a repo (clone → `install.sh`) or as an npm package referenced from the
config's `plugin` array. Commands/agents/skills then ride alongside as config files.

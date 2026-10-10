# Stack

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-10-10

## Tech Stack

| Category | Details |
|----------|---------|
| Language | Python 3 (`scripts/fetch_youtube.py`) + Markdown (all skills, persona template, docs) + JavaScript (opencode port's ESM plugin) |
| Runtime 1 — Claude Code | Plugin runtime — skills are instruction files Claude follows, not executed code, except the one bundled Python script. Commands registered from `.claude-plugin/plugin.json` |
| Runtime 2 — OpenCode | Hybrid bundle: `commands/*.md` + `agents/*.md` + `skills/*.md` config files, plus a small **dependency-free** ESM JS plugin (`plugin/plugin.js`) for the two things config files can't do (resolve the portable data dir, persist session/preset JSON). Installed via `opencode-plugin/install.sh`, which links the bundle into `~/.config/opencode` (repo stays the single source of truth) and writes a shim for the plugin entry |
| Framework | Claude Code Plugin format — `.claude-plugin/plugin.json` (manifest) + `.claude-plugin/marketplace.json` (this repo doubles as its own marketplace, `source: "./"`) |
| Database | None — personas are plain files on disk, no DB |
| External CLI dependency | `yt-dlp` (required for transcript pulling; without it, builds fall back to web-research-only) |
| Optional Python dependency | `youtube-transcript-api` (per-video fallback if `yt-dlp` caption fetch fails) |
| OpenCode port deps | None — the plugin has no runtime dependencies (no `bun install` step; `@opencode-ai/plugin` was dropped in the v2 port) |
| Dev Tools | git |
| Deployment | Claude Code: marketplace (`/plugin marketplace add YahyaZekry/Agora-RoundTable` → `/plugin install agora@agora-roundtable`). OpenCode: `bash opencode-plugin/install.sh` then restart opencode |

---

## Dev Commands

| Command | What It Does |
|---------|-------------|
| `python3 scripts/fetch_youtube.py --channel <URL> --max-videos 12 --out <dir>` | Pull a channel's videos, download captions via `yt-dlp`, write `transcripts/*.md` + `videos.json` |
| `python3 scripts/fetch_youtube.py --search "<query>" --max-videos 8 --out <dir>` | Same, but finds long-form videos OF a person across all of YouTube (no channel of their own) |
| `python3 scripts/fetch_youtube.py --videos <URL1> <URL2> --out <dir>` | Fetch specific known video URLs |
| `/coach <name>` (in Claude Code, plugin installed) | End-to-end: build or load a persona, start talking to them |
| `/coach-refresh <name>` | Wipe and rebuild a persona's plugin-owned cache from fresh research |

No build step, no test suite, no lockfile — this is a plugin repo (skills + one script), not an application.

---

## Environment Variables

| Variable | Used In | What It Enables |
|----------|---------|----------------|
| `${AGORA_DATA_DIR}` | `opencode-plugin/lib/data-dir.js` (highest precedence) + all `skills/*/SKILL.md` (Step 0) | Explicit override for the shared persona data dir (a synced or custom location). When unset, the default is `~/.agora` |
| `${CLAUDE_PLUGIN_ROOT}` | `skills/coach/SKILL.md` (Steps 3, 5) | Resolves the absolute path to `scripts/fetch_youtube.py` and `skills/coach/references/persona-template.md` regardless of where the plugin is installed |
| `${CLAUDE_PLUGIN_DATA}` | Legacy only — read, never written | The Claude Code plugin data dir. Now a legacy persona location; data is moved to `~/.agora` once and never written back |
| `${OPENCODE_CONFIG}` | Legacy only — read bridge | Base for the old opencode-native data dir (`$OPENCODE_CONFIG/agora`) that `lib/data-dir.js` still reads as a migration bridge; not used for new writes |

### Portable persona data dir (both runtimes)

`opencode-plugin/lib/data-dir.js` resolves the single shared personas directory in this
order (agent-neutral, so opencode, Claude, codex, and any other agent share one set of
people):

1. `$AGORA_DATA_DIR` (env override — a synced or custom location)
2. `~/.agora` (the neutral default; identical on Linux, macOS, and Windows)

Older installs kept personas under the Claude plugin data dir or `~/.config/opencode/agora`;
`lib/data-dir.js` still reads the latter as a bridge and `install.sh` migrates the data into
`~/.agora` once. Those legacy locations are never written to again.

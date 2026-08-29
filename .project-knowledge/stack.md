# Stack

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-29

## Tech Stack

| Category | Details |
|----------|---------|
| Language | Python 3 (`scripts/fetch_youtube.py`) + Markdown (all skills, persona template, docs) + JavaScript (opencode port's ESM plugin) |
| Runtime 1 — Claude Code | Plugin runtime — skills are instruction files Claude follows, not executed code, except the one bundled Python script. Commands registered from `.claude-plugin/plugin.json` |
| Runtime 2 — OpenCode | Hybrid bundle: `commands/*.md` + `agents/*.md` + `skills/*.md` config files, plus a small ESM JS plugin (`plugin/plugin.js`, built on `@opencode-ai/plugin`) for the two things config files can't do (resolve the portable data dir, persist session/preset JSON). Installed via `opencode-plugin/install.sh`, which symlinks the bundle into `~/.config/opencode` (repo stays the single source of truth) |
| Framework | Claude Code Plugin format — `.claude-plugin/plugin.json` (manifest) + `.claude-plugin/marketplace.json` (this repo doubles as its own marketplace, `source: "./"`) |
| Database | None — personas are plain files on disk, no DB |
| External CLI dependency | `yt-dlp` (required for transcript pulling; without it, builds fall back to web-research-only) |
| Optional Python dependency | `youtube-transcript-api` (per-video fallback if `yt-dlp` caption fetch fails) |
| OpenCode port deps | `bun` (run `bun install` in `opencode-plugin/` for `@opencode-ai/plugin`) |
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
| `${CLAUDE_PLUGIN_DATA}` | All `skills/*/SKILL.md` (Step 0 in `coach`, referenced by the others) | Primary persona-cache location on the Claude side, survives plugin updates. Personas live at `${CLAUDE_PLUGIN_DATA}/agora-roundtable/personas/`. Falls back to `~/.claude/agora-roundtable/personas` when unset |
| `${CLAUDE_PLUGIN_ROOT}` | `skills/coach/SKILL.md` (Steps 3, 5) | Resolves the absolute path to `scripts/fetch_youtube.py` and `skills/coach/references/persona-template.md` regardless of where the plugin is installed |
| `${AGORA_DATA_DIR}` | `opencode-plugin/lib/data-dir.js` (preferred first) | Explicit override for where personas live in the opencode port. Highest-precedence resolution on that side |
| `${OPENCODE_CONFIG}` | `opencode-plugin/lib/data-dir.js` | Base for the opencode-native default data dir (`$OPENCODE_CONFIG/agora`); defaults to `~/.config/opencode/agora` when unset |

### Portable persona data dir (both runtimes)

`opencode-plugin/lib/data-dir.js` resolves the single shared personas directory in this
order (so a persona built by Claude's `/coach` is instantly usable in opencode and vice
versa, but opencode never *requires* Claude):

1. `$AGORA_DATA_DIR` (env override)
2. `$CLAUDE_PLUGIN_DATA/agora-roundtable` — only if its `personas/` already exists
3. `~/.config/opencode/agora` (opencode-native default)
4. `~/.claude/agora-roundtable` (legacy Claude fallback, only if it exists)

`install.sh` symlinks `~/.config/opencode/agora/personas` → the Claude dir when present.

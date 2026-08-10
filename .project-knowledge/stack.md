# Stack

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10

## Tech Stack

| Category | Details |
|----------|---------|
| Language | Python 3 (`scripts/fetch_youtube.py`) + Markdown (all 5 skills, persona template, docs) |
| Runtime | Claude Code plugin runtime — skills are instruction files Claude follows, not executed code, except the one bundled Python script |
| Framework | Claude Code Plugin format — `.claude-plugin/plugin.json` (manifest) + `.claude-plugin/marketplace.json` (this repo doubles as its own marketplace, `source: "./"`) |
| Database | None — personas are plain files on disk, no DB |
| External CLI dependency | `yt-dlp` (required for transcript pulling; without it, builds fall back to web-research-only) |
| Optional Python dependency | `youtube-transcript-api` (per-video fallback if `yt-dlp` caption fetch fails) |
| Dev Tools | git |
| Deployment | Distributed via Claude Code plugin marketplace (`/plugin marketplace add <owner>/talk-to-anyone`, `/plugin install talk-to-anyone@talk-to-anyone`) |

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
| `${CLAUDE_PLUGIN_DATA}` | All 5 `skills/*/SKILL.md` (Step 0 in `coach`, referenced by the others) | Primary persona-cache location, survives plugin updates. Falls back to `~/.claude/talk-to-anyone/personas` when unset (repo used standalone, not as an installed plugin) |
| `${CLAUDE_PLUGIN_ROOT}` | `skills/coach/SKILL.md` (Steps 3, 5) | Resolves the absolute path to `scripts/fetch_youtube.py` and `skills/coach/references/persona-template.md` regardless of where the plugin is installed |

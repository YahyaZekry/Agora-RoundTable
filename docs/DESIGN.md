# Design — talk-to-anyone

Built 2026-07-06 (overnight autonomous build). Decisions confirmed with Colton before
the run: Claude Code plugin format, bundled yt-dlp fetcher, repo name `talk-to-anyone`,
cached personas.

## Shape

A single-plugin repo that doubles as its own marketplace (`.claude-plugin/marketplace.json`
with `source: "./"`). Five skills, one Python script, zero runtime services:

- **skills/coach** — the whole product: resolve name → check cache → find channel →
  run fetcher → read transcripts + web research → write persona.md → embody.
- **skills/coach-switch / coach-end / coach-list / coach-refresh** — thin session
  controls that reuse the coach workflow by reference instead of duplicating it.
- **scripts/fetch_youtube.py** — deterministic part of the pipeline. yt-dlp for channel
  listing (popularity-sorted tab, recent-uploads fallback) and captions (manual subs
  preferred, auto-captions fallback, VTT → deduped plain text). Optional
  youtube-transcript-api as a per-video fallback. No API keys.

## Key decisions

- **Persona = markdown file, not fine-tuning or RAG.** A 2-3k-word structured persona
  (voice rules + beliefs + named frameworks + verbatim quotes + embodiment rules) is
  enough for Claude to hold a voice, is human-inspectable, and costs nothing to store.
- **Cache in `${CLAUDE_PLUGIN_DATA}`** (survives plugin updates), fallback
  `~/.claude/talk-to-anyone/` when the variable doesn't substitute (repo used without
  plugin install). Raw transcripts are kept next to the persona so a rebuild or a
  deeper question ("what exactly did he say about X?") can re-read them.
- **Active coach is conversation state, not disk state.** No lock files; two parallel
  chats can talk to two different coaches. /coach-end only drops character, never data.
- **Fabrication guardrails live in the persona file itself** (Embodiment Rules), so
  they travel with the cache and survive plugin updates.

## Failure routes

- No yt-dlp → tell user the install command; offer web-research-only persona.
- Zero captions (disabled/region) → web-research-only persona, noted in the file.
- Ambiguous name → resolve to most prominent match, state the assumption in one line.
- No YouTube channel at all → web-research-only persona.

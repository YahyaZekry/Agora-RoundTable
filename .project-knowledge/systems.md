# Systems

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10
> This isn't a web app — the standard categories below mostly don't apply. Rows are
> relabeled to this project's actual cross-cutting concerns instead of forced into
> auth/DB/payments boxes that don't exist here.

| System | Status | Details |
|--------|--------|---------|
| Authentication | N/A | No auth — local CLI/plugin, no accounts |
| Database | N/A | No DB — persona cache is plain files on disk |
| Email | N/A | — |
| Payments | N/A | — |
| **Persona cache (storage)** | Active | `${CLAUDE_PLUGIN_DATA}/personas/<slug>/`, legacy fallback `~/.claude/talk-to-anyone/personas/`. No lock files — active coach is conversation state, not disk state (two parallel chats can talk to two different coaches) |
| **YouTube caption fetching** | Active | `scripts/fetch_youtube.py` via `yt-dlp` (manual subs preferred, auto-captions fallback), optional `youtube-transcript-api` per-video fallback. Zero-API-key design |
| Realtime | N/A | — |
| Background Jobs | N/A | — |
| **Web research** | Active | Not code — Claude's own live web search, run live during a `/coach` build (Step 4). As of v1.2.0, organized per domain and persisted to `research/` instead of being distilled-then-discarded |
| **AI / persona embodiment** | Active | The actual product: Claude reads `persona.md` + (v1.2.0) `research/` on demand and speaks in-character. Fabrication guardrails live inside the persona file itself (Embodiment Rules), so they travel with the cache and survive plugin updates |

# Systems

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-29
> This isn't a web app — the standard categories below mostly don't apply. Rows are
> relabeled to this project's actual cross-cutting concerns instead of forced into
> auth/DB/payments boxes that don't exist here.

| System | Status | Details |
|--------|--------|---------|
| Authentication | N/A | No auth — local CLI/plugin, no accounts |
| Database | N/A | No DB — persona cache is plain files on disk |
| Email | N/A | — |
| Payments | N/A | — |
| **Persona cache (storage)** | Active | Portable across both runtimes via `opencode-plugin/lib/data-dir.js`. Claude side: `${CLAUDE_PLUGIN_DATA}/agora-roundtable/personas/<slug>/`; opencode side: `~/.config/opencode/agora/personas/<slug>/` (or `$AGORA_DATA_DIR/personas/...`, or the Claude dir when symlinked). No lock files — active coach is conversation state, not disk state (two parallel chats can talk to two different coaches) |
| **Portable data-dir resolver** | Active | `opencode-plugin/lib/data-dir.js` — the single source of truth for persona/session/preset paths on the opencode side, and the authority the Claude side's `${CLAUDE_PLUGIN_DATA}` fallback agrees with. Opencode's `plugin/plugin.js` exposes `agora_data_dir` so commands can resolve paths at runtime |
| **OpenCode JS plugin** | Active | `opencode-plugin/plugin/plugin.js` (ESM, `@opencode-ai/plugin`) exposes three tools: `agora_data_dir` (resolve paths), `agora_slugify` (name → slug), `agora_session` (read/write `roundtable-session.json` + `roundtable-presets.json`). This is the only place opencode has real runtime code — everything else (commands/agents/skills) is declarative config |
| **YouTube caption fetching** | Active | `scripts/fetch_youtube.py` via `yt-dlp` (manual subs preferred, auto-captions fallback), optional `youtube-transcript-api` per-video fallback. Zero-API-key design |
| Realtime | N/A | — |
| Background Jobs | N/A | — |
| **Web research** | Active | Not code — the host model's own live web search, run live during a `/coach` (or `/agora coach`) build (Step 4). As of v1.2.0, organized per domain and persisted to `research/` instead of being distilled-then-discarded |
| **AI / persona embodiment** | Active | The actual product: the host model reads `persona.md` + (v1.2.0) `research/` on demand and speaks in-character. Fabrication guardrails live inside the persona file itself (Embodiment Rules), so they travel with the cache and survive plugin updates |

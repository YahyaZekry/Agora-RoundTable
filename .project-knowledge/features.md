# Features & Workflows

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10

## Features

- **`/coach <name>`** — build (first time) or load (cached) a persona and start talking to them in character. *(v1.0.0)*
- **`/coach-switch <name>`** — close out the current coach, start/load a different one, no need for `/coach-end` first. *(v1.0.0)*
- **`/coach-end`** — drop character, back to normal Claude, cache untouched. *(v1.0.0)*
- **`/coach-list`** — show every persona already built on this machine (name, build date, source-video count). *(v1.0.0)*
- **`/coach-refresh <name>`** — wipe a persona's plugin-owned cache (`persona.md`, `videos.json`, `transcripts/`, and as of v1.2.0 `research/`) and rebuild from fresh research, leaving any non-plugin file in the folder untouched. *(v1.0.0, extended v1.2.0)*

---

## Workflows

**Building a persona from scratch (`/coach <name>`, no cache hit)**
1. Identify the real person + their 1-4 distinct domains of public authority — `skills/coach/SKILL.md` Step 1 *(domain identification added v1.2.0)*
2. Find their spoken content, if any (own channel, or interviews of them elsewhere) — Step 2
3. Pull real transcripts via `scripts/fetch_youtube.py`, write `transcripts/*.md` — Step 3
4. Deep web research, run per domain, persisted to `research/<domain>.md` or `research/<domain>/` — Step 4 *(persistence + per-domain split added v1.2.0)*
5. Distill everything into `persona.md`, including a Deep-Dive Sources index pointing at what's on disk — Step 5
6. Embody: one-time handoff line, then speak in character; for anything deeper than the compressed summary, read the relevant `research/` file or transcript live — Step 6 *(live-read-for-depth added v1.2.0)*

**Multi-lane figure vs. single-lane figure**
A person known for genuinely separate things (e.g. marketing AND content creation) gets research organized as `research/<domain>/` — one folder per domain. A single-lane figure (most people; e.g. a philosopher, an investor with one clear discipline) gets one flat `research/<domain-slug>.md` — no forced splitting.

**Explicitly out of scope for this repo**
Noticing/incorporating files a user already has sitting in a persona's folder *before* a build runs. That's left to whatever's managing that folder externally (e.g. a vault-sync skill) — this plugin's own research pipeline doesn't duplicate it.

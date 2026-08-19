# Features & Workflows

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10

## Features

- **`/coach <name>`** — build (first time) or load (cached) a persona and start talking to them in character. *(v1.0.0)*
- **`/coach-switch <name>`** — close out the current coach, start/load a different one, no need for `/coach-end` first. *(v1.0.0)*
- **`/coach-end`** — drop character, back to normal Claude, cache untouched. *(v1.0.0)*
- **`/coach-list`** — show every persona already built on this machine (name, build date, source-video count). *(v1.0.0)*
- **`/coach-refresh <name>`** — wipe a persona's plugin-owned cache (`persona.md`, `videos.json`, `transcripts/`, `research/`, and the `inbox/_sync-status.md` manifest) and rebuild from fresh research + re-extract everything currently in `inbox/`, leaving the dropped files themselves untouched. *(v1.0.0, extended v1.2.0, v1.2.2)*

---

## Workflows

**Building a persona from scratch (`/coach <name>`, no cache hit)**
1. Identify the real person + their 1-4 distinct domains of public authority — Step 1 *(domain identification added v1.2.0)*
2. Find their spoken content, if any (own channel, or interviews of them elsewhere) — Step 2
3. Pull real transcripts via `scripts/fetch_youtube.py`, write `transcripts/*.md` — Step 3
4. Deep web research, run per domain, persisted flat to `research/<domain-slug>.md` — Step 4 *(persistence v1.2.0, flattened v1.2.1)*. Written directly by whoever read the primary source — never a compressed report handed to someone else to write from (that lossy hop is what Step 4.5 exists to catch when it slips through anyway).
5. **Verify `research/<domain-slug>.md` against the actual sources, independently, before proceeding** — mandatory, not skippable — Step 4.5 *(added v1.2.3, after real content loss found on two separate builds; extended v1.2.4)*. Four checks: missing frameworks, flattened origin stories/numbers, quotes that aren't verbatim in their credited source, and — added v1.2.4 — claims with no source in the folder at all (recalled from the person's books rather than read), which get relocated to a labeled section so embodiment hedges instead of quoting. Sources checked include `inbox/`, not just `transcripts/` and web claims.
6. Distill everything into `persona.md`, including a Deep-Dive Sources index listing each `research/` file — Step 5
7. **Check `inbox/`** — every invocation, cache hit or fresh build alike: extract anything Yahya dropped in (notes, a dossier, a PDF) into the matching `research/<domain>.md`, tracked via `inbox/_sync-status.md` — Step 5.5 *(added v1.2.2, coverage tracking v1.2.4)*. The manifest records coverage, not just a synced date: logging a file complete requires walking its actual structure and confirming each section landed in `research/`; anything sampled (every PDF) is logged partial with the remainder named, and partial is a re-extraction trigger. Read in full by whoever's doing the extraction directly — same no-delegated-summary rule as Step 4.
8. Embody: one-time handoff line, then speak in character; for anything deeper than the compressed summary, match the question's topic to a domain and read that `research/<domain>.md` live — a lookup, not a guess — Step 6 *(live-read v1.2.0, made topic-matched + transcripts/inbox excluded v1.2.1/v1.2.2)*

**Cache-hit path (`/coach <name>` again)**
Skips straight to Step 5.5 — so even an already-built persona picks up anything newly
dropped into its `inbox/` before embodying. Not a one-time build step.

**Multi-domain vs. single-domain figures**
A person known for genuinely separate things (e.g. marketing AND wealth philosophy)
gets one flat `research/<domain-slug>.md` per domain. A single-domain figure gets just
one file. No subfolder nesting regardless of domain count (v1.2.1).

**What's still explicitly out of scope for this repo**
Only one thing now: moving a built persona OUT of the plugin's own data dir and INTO
an external vault/notes system, and deciding where it belongs there. That's
inherently specific to whatever vault-management setup the user has (a `persona-sync`
skill, in Yahya's case) — the plugin has no concept of "vault" and shouldn't gain one,
or it stops being portable to anyone else who installs it. *(scope re-confirmed v1.2.2,
after inbox/extraction itself was pulled back IN — see history.md)*

# Features & Workflows

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-30

## Dual-runtime — identical capabilities

The product ships for **two hosts** with the same feature set and the **same persona
format and shared data dir**:

- **Claude Code** — commands provided by `skills/*` (e.g. `/coach`, `/roundtable`, `/discuss`).
- **OpenCode** — the `opencode-plugin/` port mirrors every command under `/agora*`
  (e.g. `/agora coach`, `/agora roundtable`, `/agora discuss`), sharing the personas
  directory so a coach built in one host is usable in the other. The opencode side uses
  `agents/agora-*` subagents for the same agent-based roundtable, and the JS plugin
  (`plugin/plugin.js`) for path/session resolution. Persona-building steps are identical.

Below, "the command" refers to either runtime's equivalent.

## Features

**Single-coach commands:**
- **`/coach <name>`** — build (first time) or load (cached) a persona and start talking to them in character. Also ensures `inbox/` exists. *(v1.0.0)*
- **`/coach-switch <name>`** — close out the current coach, start/load a different one, no need for `/coach-end` first. *(v1.0.0)*
- **`/coach-end`** — drop character, back to normal Claude, cache untouched. *(v1.0.0)*
- **`/coach-list`** — show every persona already built on this machine (name, build date, source-video count) + saved roundtable presets. *(v1.0.0, presets v2.1.0)*
- **`/coach-refresh <name>`** — rebuild a persona from fresh research. **Moves the old cache to `.refresh-backup/` rather than deleting it**, builds, verifies the result, and only then discards the backup; on any failure it restores and reports, so a failed refresh can never destroy a persona (v2.5.1). Restores old transcripts if a fresh fetch returns none. Runs `/coach-update` after the build. `inbox/` files are never touched. *(v1.0.0, extended v1.2.0–v1.2.4, inbox-update-on-refresh v2.2.0, non-destructive v2.5.1)*
- **`/coach-refresh-all [preset]`** — rebuild every built coach (no argument), or every coach in a named preset. **Delegates to `/coach-refresh` rather than restating its steps**, so it inherits the backup-and-restore behaviour; a coach whose build fails is restored and the run continues to the next one. Warns upfront: slow (several minutes per coach). `inbox/` files are never touched. *(v2.3.0, delegating + non-destructive v2.5.1)*
- **`/coach-update <name>`** — inbox sync **and the command that closes gaps**: merges new `inbox/` files into `research/<domain>.md`, mines `transcripts/` for open `unmined` gaps, then offers a consent-gated web-research pass for anything still open. Strictly additive — never deletes or rebuilds. Runs even when the inbox is empty. Updates `_sync-status.md`. *(v2.2.0, gap-closing v2.5.1)*
- **`/coach-update-all [preset]`** — run the **full** `/coach-update` flow (inbox sync *and* gap closing) for every built coach, or every coach in a named preset. Differs from the single-coach version in one way: it does not stop to ask before web research per coach — it collects every gap needing research across all coaches and asks once at the end. *(v2.3.0, gap-closing v2.5.1)*

**Roundtable commands:**
- **`/roundtable <name1>, <name2>, ...`** — start a multi-coach session with two or more already-built personas. Coaches must exist in cache; if any are missing, the skill tells the user to build them first with `/coach`. Writes `DATA_DIR/roundtable-session.json` to persist the active roster. *(v2.0.0)*
- **`/roundtable <preset-name>`** — load a named preset instead of listing coaches by name (e.g. `/roundtable y-table`). *(v2.1.0)*
- **`/roundtable-save <preset-name>`** — save the current active session as a named preset, or define a new preset with `<preset-name> name1, name2, ...`. Stored in `DATA_DIR/roundtable-presets.json`. *(v2.1.0)*
- **`/roundtable-add <name>`** — add a coach to an active roundtable mid-conversation. Updates the session JSON. *(v2.0.0)*
- **`/roundtable-remove <name>`** — remove a coach from the active roundtable. If one coach remains, asks the user whether to continue or switch to `/coach`. *(v2.0.0)*
- **`/roundtable-end`** — delete `roundtable-session.json`, drop all personas, back to normal Claude. Cache untouched. *(v2.0.0)*

---

## Workflows

**Building a persona from scratch (`/coach <name>`, no cache hit)**
1. Identify the real person + their 1-4 distinct domains of public authority — Step 1 *(domain identification added v1.2.0)*
2. Ensure `DATA_DIR/<slug>/inbox/` exists (create if not) — Step 1 *(added v2.2.0; was implicit before, now explicit)*
3. Find their spoken content, if any (own channel, or interviews of them elsewhere) — Step 2
4. Pull real transcripts via `scripts/fetch_youtube.py`, write `transcripts/*.md` — Step 3
5. Deep web research, run per domain, persisted flat to `research/<domain-slug>.md` — Step 4 *(persistence v1.2.0, flattened v1.2.1)*. Written directly by whoever read the primary source — never a compressed report handed to someone else to write from.
6. **Verify `research/<domain-slug>.md` against the actual sources, independently, before proceeding** — mandatory, not skippable — Step 4.5 *(added v1.2.3)*. Four checks: missing frameworks, flattened origin stories/numbers, verbatim quotes that don't match their credited source, and claims with no source in the folder at all (relocated to a labeled "no primary source" section so embodiment hedges instead of quoting, v1.2.4).
7. Distill everything into `persona.md`, including a Deep-Dive Sources index listing each `research/` file — Step 5
8. Embody: one-time handoff line, then speak in character; for anything deeper than the compressed summary, match the question's topic to a domain and read that `research/<domain>.md` live — a lookup, not a guess — Step 6 *(live-read v1.2.0)*

**Cache-hit path (`/coach <name>` again)**
Reads persona.md and goes straight to embodiment (Step 6). Inbox is no longer auto-processed
on cache hits — call `/coach-update <name>` explicitly when you've dropped something new. *(inbox
moved to explicit in v2.2.0)*

**Inbox sync and gap-closing (`/coach-update <name>`)** *(gap steps added v2.5.1)*
1. Locate `DATA_DIR/<slug>/inbox/`; read `_sync-status.md` to know what's already been extracted.
   An empty inbox does NOT abort the command — it continues to the gap steps below.
2. For each new or partial file: text files read in full, PDFs first 1-3 pages; extract content
   into the matching `research/<domain>.md` directly (no intermediary report)
3. Update `_sync-status.md`: file, date, coverage (complete/partial), target `research/` file.
   Partial coverage is a re-extraction trigger — logged partial rather than guessing complete.
4. **Close `unmined` gaps** — content already in `transcripts/` that never reached `research/`.
   Free, no web. This is why an empty inbox must not stop the command.
5. **Close `user-only` gaps** the freshly-synced inbox files fill.
6. **Offer a consent-gated research pass** for anything still open, scoped to those gaps only.
   Strictly additive: never deletes or rebuilds persona.md, videos.json, transcripts/ or
   existing research/. `/coach-refresh` is for wanting a fresh build, not for filling a hole.
7. Report what was synced and which gaps closed; resume session if a coach was active

**Multi-domain vs. single-domain figures**
A person known for genuinely separate things gets one flat `research/<domain-slug>.md` per domain.
A single-domain figure gets just one file. No subfolder nesting regardless of domain count (v1.2.1).

**Named roundtable presets (`/roundtable-save`, `/roundtable <preset>`)**
`DATA_DIR/roundtable-presets.json` stores named presets as a plain JSON object: `{ "y-table": ["thomas-harris", "joe-navarro"] }`. `/roundtable <name>` checks for a preset match before parsing as comma-separated coach names. Human-readable and editable directly. *(v2.1.0)*

**Roundtable session state**
The active roster is persisted in `DATA_DIR/roundtable-session.json`:
```json
{ "coaches": [{ "slug": "thomas-harris", "name": "Thomas Harris" }, ...] }
```
`/roundtable-add` and `/roundtable-remove` update this file mid-conversation. The
facilitator reads it at the start of each message to know who's in the room.

**Three message modes inside a roundtable (v2.4.0 — agent-based):**

Each coach runs as a **dedicated Agent** with its own independent context window — not Claude switching voices in the same window. The facilitator spawns agents, collects responses, and synthesizes. It never writes a coach response itself.

1. **General** (default) — all coach agents spawn in parallel (one Agent per coach, same response turn, `run_in_background: false`). Each reads only its own `persona.md` and the most relevant `research/<domain>.md`. Independent, uncontaminated by what others say. Facilitator displays responses in sequence and notes key tensions.
2. **Direct** (`@name ...`) — one dedicated Agent for that coach only. Reads its own files, responds in character.
3. **Facilitated discussion** (`/discuss <topic>`) — agents run sequentially. Each agent's prompt includes the prior agents' actual responses as context before it generates its own. Real reaction, not a scripted exchange.

**What's explicitly out of scope for this repo**
Moving a built persona OUT of the plugin's own data dir and INTO an external vault/notes
system. That's inherently specific to whatever vault-management setup the user has (a
`persona-sync` skill, in Yahya's case) — the plugin has no concept of "vault" and
shouldn't gain one, or it stops being portable to anyone else who installs it.
*(scope re-confirmed v1.2.2, v2.0.0)*

# History

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-22
> Past-only. Append-only — never delete entries.

## Removed

- ~~`research/<domain-slug>/<domain-slug>.md` per-domain subfolder option~~ — existed
  for a "domain outgrows one file" case that never happened; just added a redundant
  folder+file with the same name. Always flat `research/<domain-slug>.md` now.
  *(removed: 2026-08-10, v1.2.1)*

---

## Fixed

- **Silent content loss from double-summarization** — two separate real persona builds
  (Alex Hormozi, David Goggins) had research written by compressing a subagent's
  *report* of the primary transcripts instead of the transcripts themselves. Both
  looked complete on read-through; both had real gaps (Goggins: 2 entire named
  frameworks missing outright, every origin story flattened to generic paraphrase, one
  fabricated quote) caught only by an independent verification pass against the raw
  sources. Not a one-off mistake — structural (two lossy hops compound even when each
  looks fine alone). *(fixed: 2026-08-11, v1.2.3 — Step 4.5)*

---

## Decisions

- **Persist deep research per domain instead of discarding it into `persona.md`** — the
  template's 1,500-3,000-word budget is right for voice, but Step 4's web research was
  being distilled in and thrown away, with no way to go deeper than the summary later.
  Fix: `research/<domain>.md`, plus a Deep-Dive Sources index in `persona.md` and a
  live-read instruction at embodiment time. Real gap confirmed by comparing against
  this repo's own bundled `examples/alex-hormozi/persona.md` and
  `examples/warren-buffett/persona.md` — dense, well-sourced examples that proved the
  *format* could hold real depth; the problem was research getting thrown away, not
  the format's ceiling. *(2026-08-10, v1.2.0)*
- **Transcripts written as Markdown + frontmatter, not plain `.txt`** — `.md` renders
  properly and is self-descriptive (title, url, duration, view count, caption source,
  word count) when opened directly, not just parsed as raw input. *(2026-08-10, v1.1.x)*
- **Dropped the per-domain-subfolder option, always flat `research/<domain-slug>.md`**
  — see Removed above. *(2026-08-10, v1.2.1)*
- **`transcripts/` demoted from live reference to archival-only** — Step 6 used to say
  "read `research/<domain>` (or a transcript)" when a question needed depth, leaving it
  to judgment which to check. Now: transcripts are raw intake, mined into `research/`
  and then archival; depth lookups are topic-matched straight to
  `research/<domain>.md`, never a second vague option. *(2026-08-10, v1.2.1)*
- **Reversed: pre-existing-file/inbox handling moved INTO the plugin, not left out of
  scope.** Originally decided this belonged to external vault-side tooling only
  (`persona-sync`) — wrong call. "Drop your own notes for the AI to fold into this
  person's research" isn't Obsidian-specific, it's a generic capability of the persona
  pipeline itself. `inbox/` is now standard folder shape; Step 5.5 checks it on every
  `/coach` invocation (cache hit or not) and extracts into `research/<domain>.md` via
  the same mechanism Step 4 uses. Tracked in `inbox/_sync-status.md` (a manifest, not
  frontmatter — PDFs can't hold YAML frontmatter). What's still genuinely external:
  only moving a built persona INTO a vault and deciding where — that stays with
  vault-side tooling since the plugin has no concept of "vault" and shouldn't gain one.
  *(2026-08-10, v1.2.2, supersedes the "explicitly out of scope" decision from earlier
  the same day)*
- **Verification has to cover sourcing and coverage, not just accuracy.** Step 4.5
  (v1.2.3) was built to catch content loss and fabricated quotes, and it does. Running
  it retroactively against the Hormozi persona — built before it existed — found
  neither: every verbatim traced word-for-word. It found two things Step 4.5 was blind
  to instead. (1) `inbox/_sync-status.md` recorded *whether* a file was synced but not
  *how much* of it was extracted, so a 13-concept dossier logged as done after 5
  permanently stopped later passes from looking — Step 5.5, Step 4.5 and
  `/coach-refresh` all trust that manifest, so a false "complete" is terminal, worse
  than no entry. Coverage is now a required column, defensible by walking the source's
  structure; partial is the default for anything sampled and is itself a re-extraction
  trigger. (2) Step 4.5 compared `research/` against its sources but never asked which
  claims had *no* source in the folder — book frameworks recalled from training rather
  than read from anything present. That's the hardest class to catch precisely because
  the claims are usually true; the defect is presenting them as sourced. They're now
  relocated to a labeled section rather than deleted, so Step 6 hedges instead of
  quoting. *(2026-08-19, v1.2.4)*
- **A retroactive verification pass is worth running on every persona built before
  v1.2.3, not just ones that feel thin.** Hormozi felt fine and read fine — the gaps
  were 8 unmined concepts and 5 unsourced frameworks, invisible from the output side.
  *(2026-08-19)*
- **Detached fork, made the repo fully independent.** `YahyaZekry/talk-to-anyone` was a
  fork of `coltonjosephdean-rgb/talk-to-anyone`. User detached it on GitHub (Settings →
  Detach fork). `plugin.json` and `marketplace.json` updated to credit Yahya Zekry as
  author, with a `based_on` field pointing to the original. `LICENSE` kept untouched
  (MIT requires preserving the original copyright notice). README updated: install
  command now points to `YahyaZekry/talk-to-anyone`, Colton's personal narrative removed,
  attribution section added. *(2026-08-22, v2.0.0)*
- **Added roundtable feature** — four new skills: `roundtable`, `roundtable-add`,
  `roundtable-remove`, `roundtable-end`. Roundtable runs multiple already-built personas
  simultaneously. The facilitator (Claude, out of character) handles three message types:
  general (all coaches respond in sequence), direct (@name routes to one), and
  /discuss (structured facilitated exchange where coaches react to each other, followed
  by a synthesis). Session state persisted in `DATA_DIR/roundtable-session.json` so
  add/remove can modify the roster mid-conversation. Coaches must be pre-built — the
  skill does not auto-build, it tells the user to run `/coach <name>` first. Bumped to
  v2.0.0. *(2026-08-22)*
- ~~**Plugin name still undecided.**~~ Decided: renamed to `agora-roundtable`. Updated
  both JSON manifests, all skill fallback DATA_DIR paths (`~/.claude/agora-roundtable/personas`),
  display name in README install command. GitHub repo renamed accordingly. *(2026-08-22/23, v2.0.0→)*
- **Named roundtable presets** — `/roundtable <preset>` now checks `DATA_DIR/roundtable-presets.json`
  before parsing as comma-separated names. `/roundtable-save` writes/updates presets. `/coach-list`
  also shows saved presets. Preset file is plain JSON, human-editable. Preset exists as an opt-in
  layer — if the file doesn't exist, `/roundtable` behavior is unchanged. *(2026-08-23, v2.1.0)*
- **Inbox processing moved out of `/coach` into explicit `/coach-update`** — Step 5.5 (auto-process
  `inbox/` on every `/coach` invocation, cache hit or not) was removed. Problem: implicit, always-on
  behavior where `/roundtable` (which skips the build pipeline entirely and loads from cache) never
  processed inboxes at all — silent inconsistency the user had to know about. New `/coach-update`
  skill owns inbox processing exclusively. `/coach-refresh` now explicitly calls `/coach-update`
  logic as its final step so a full rebuild still picks up inbox material. *(2026-08-23, v2.2.0)*
- **Bulk inbox and refresh commands** — `/coach-update-all [preset]` and `/coach-refresh-all [preset]`
  added. Both accept an optional preset name to scope the operation; without an argument they operate
  on all slugs in DATA_DIR with a `persona.md`. `/coach-refresh-all` warns upfront: slow (minutes per
  coach). `inbox/` files are never deleted by any command. *(2026-08-23, v2.3.0)*
- **Roundtable rewritten to use real Agent subagents** — the original roundtable had Claude switch
  voices inline in the same context, which is fabrication, not embodiment. Rewritten: each coach
  gets a dedicated Agent with its own independent context window. Each agent reads only its own
  `persona.md` and the relevant `research/<domain>.md` — no visibility into what others say (for
  general questions) or explicit context of prior responses (for `/discuss`). The facilitator spawns
  agents, collects responses, and synthesizes; it never writes a coach response itself. Three message
  modes: general (all agents in parallel), @direct (one agent), /discuss (sequential — each agent
  gets prior agents' actual responses as context). *(2026-08-23, v2.4.0)*
- **`inbox/` folder creation made explicit in `/coach`** — v1.2.2 said "created on every build" but
  the skill never had an explicit mkdir step; the implicit creation came from Step 5.5 (which was then
  removed in v2.2.0). Added an explicit `mkdir -p DATA_DIR/<slug>/inbox` to Step 1, runs on cache hit
  and fresh build alike. *(2026-08-23, v2.4.0 fix)*

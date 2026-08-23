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

## v1.1.0 — multi-source pipeline (2026-07-06)

YouTube demoted from requirement to add-on. Every build now runs deep web research
(books, print interviews, verified quotes); spoken content is merged in when it exists
anywhere on YouTube — own channel, or interviews of the person on other channels via
the fetcher's new `--search` mode. Historical figures are in scope: their writings are
the corpus, voice reconstructed in their era's register. Effort scales adaptively
(2-5 min builds).

## v1.2.0 — domain-organized deep research (2026-08-10)

Problem: `persona.md`'s 1,500-3,000-word budget is enough for voice, but Step 4's web
research was being distilled into it and then discarded — no way to go deeper on a
question than the compressed summary without re-researching from scratch. And a
multi-lane figure (a marketing guru who's also a content creator) got one
undifferentiated research pass instead of research organized by what they're actually
known for.

Fix: Step 1 now also identifies the person's 1-4 distinct domains of public authority.
Step 4 researches per domain and **persists** findings to one flat file per domain,
`<slug>/research/<domain-slug>.md`, instead of letting them evaporate into the
distillation. `persona.md` gets a new "Deep-Dive Sources" section indexing each
`research/` file. Step 6 (embodiment) matches a question's topic to a domain and reads
that `research/<domain-slug>.md` live — a lookup, not a depth judgment call.
`transcripts/` is raw intake, mined into `research/` and then archival — not a second
reference target once mining is done. `/coach-refresh` clears `research/` along with
the rest of the cache on rebuild.

**v1.2.1 (2026-08-10, same day)** — dropped the original per-domain-subfolder option
(`research/<domain-slug>/<domain-slug>.md`) in favor of always-flat
`research/<domain-slug>.md`. The subfolder existed for a "domain grows past one file"
case that never actually happened and just added visual clutter for no benefit — if a
domain's research genuinely outgrows one file later, that's a deliberate restructure
then, not a default now.

**v1.2.2 (2026-08-10, same day)** — added `inbox/` and Step 5.5. A user dropping their
own notes/dossier/PDF about a person for the AI to fold into that person's research
isn't Obsidian-specific or specific to any particular setup — it's a generically
useful capability, so it belongs in the plugin itself, not bolted on by
external tooling. `DATA_DIR/<slug>/inbox/` is now standard folder shape, created on
every build; Step 5.5 checks it on *every* `/coach` invocation, cache hit or not, and
extracts anything new straight into `research/<domain>.md` — same mechanism Step 4
already uses. Tracked via `inbox/_sync-status.md` (a manifest, not frontmatter — PDFs
can't hold YAML frontmatter, so this needed to be uniform across file types anyway).
`/coach-refresh` clears the manifest (not the dropped files) so a refresh re-extracts
everything current in `inbox/`.

**v1.2.3 (2026-08-11)** — added Step 4.5, a mandatory verification pass. Problem
found in practice, twice, on two different persona builds: research written by
compressing a subagent's *report* of the transcripts (rather than the transcripts
themselves) silently dropped named frameworks, origin stories, and specific numbers —
and once fabricated a quote that doesn't appear anywhere in the source. The failure
mode is structural, not a one-off: two summarization hops (source → report,
report → research file) compound losses even when each hop looks reasonable alone.
Fix: (1) Step 4 and Step 5.5 now say explicitly not to summarize a summary — whoever
reads the primary source writes `research/<domain>.md` directly; (2) Step 4.5 is a
separate, mandatory, independent check of `research/<domain>.md` against the actual
sources, every build, before `persona.md` gets written from it. Both times this was
run retroactively as a one-off "let's double check" pass, it found real gaps in
minutes — the fix is making that pass unskippable, not relying on someone getting
suspicious enough to ask for it.

**v1.2.4 (2026-08-19)** — closed two holes Step 4.5 didn't cover, both found by
running the v1.2.3 verification pass retroactively against a persona built before it
existed. (1) The manifest could lie: `_sync-status.md` recorded a file as synced with
no notion of *how much* of it was extracted, and a dossier with 13 concepts had been
logged as done after 5 — which then stopped every later pass from looking, since Step
5.5, Step 4.5 and `/coach-refresh` all trust the manifest. Fix: coverage is now a
required manifest column, defensible by walking the source's actual structure, with
partial the default for anything sampled (every PDF). (2) Step 4.5 checked what
`research/` said against its sources but never checked for claims with *no* source in
the folder — frameworks recalled from the person's books rather than read from
anything present. Those are the hardest class to spot, because they're usually true;
the defect is presenting them as sourced. Fix: a fourth check that relocates them to a
labeled section instead of deleting them, so embodiment hedges rather than quotes.
Step 4.5 also now names `inbox/` as a source to verify against, not just
`transcripts/` and web claims.

Explicitly out of scope: noticing/incorporating pre-existing files a user already has
sitting in a persona's folder before a build. That's a separate concern from this
plugin's own research pipeline — left to whatever's managing that folder externally
(e.g. a vault-sync skill), not duplicated here.

## v2.4.0 — agent-based roundtable (2026-08-23)

The roundtable was rewritten from "Claude switching voices in one context" to real
independent subagents. Each coach now runs as a dedicated Agent with its own context
window, reads only its own persona.md and research/ files, and has no visibility into
what other coaches are about to say.

Message type C (general): all coach agents spawn in parallel — independent, uncontaminated.
Message type B (/discuss): agents run sequentially — each receives the prior agents'
actual responses as context before generating their own. Real reaction, not scripted exchange.
Message type A (@name): one dedicated agent for that coach.

The facilitator (Claude in the main session) spawns the agents, collects responses,
and synthesizes. It never writes a coach response itself.

This same pattern was applied to the /novel skill's Step 5: Simon routes and synthesizes,
but never simulates a coach voice inline.

## v2.3.0 — bulk operations: /coach-update-all and /coach-refresh-all (2026-08-23)

Both commands accept an optional preset name (`/coach-update-all y-table`) to scope
the operation to one named table rather than every built coach. Without an argument
they scan DATA_DIR for every slug with a persona.md and operate on all of them.

`/coach-refresh-all` is deliberately slow and warns upfront — each coach is a full
rebuild (transcripts + research + verify + persona.md + inbox sync). `inbox/` files
are never deleted.

## v2.2.0 — explicit inbox sync with /coach-update (2026-08-23)

Problem: `/coach` processed `inbox/` on every load, including cache hits where the user
just wanted to resume a conversation. This was implicit, always-on behavior that also
meant `/roundtable` (which loads from cache and skips the build pipeline entirely) never
processed inboxes at all — inconsistency the user had to know about.

Fix: inbox processing removed from `/coach` Step 5.5 entirely. New `/coach-update`
skill owns it exclusively. Call `/coach-update <name>` whenever you've dropped
something into a coach's `inbox/` and want it folded into their research. `/coach-refresh`
now explicitly calls `/coach-update` logic as its final step after rebuilding, so a full
rebuild still picks up inbox material. `/roundtable` behavior is unchanged — if you want
inbox synced before a roundtable, run `/coach-update <name>` for each coach first.

Design constraint honored: inbox processing is now opt-in, explicit, and consistent
across both single-coach and roundtable workflows.

## v2.1.0 — named roundtable presets (2026-08-22)

Problem: a roundtable with a fixed team (e.g. "Y's table": Harris, Navarro, Sherlock,
Patrick Jane) required typing out all the names every time. For project-specific setups
with named tables, this was friction.

Fix: `DATA_DIR/roundtable-presets.json` stores named presets. `/roundtable <name>` now
checks for a preset match before parsing as comma-separated names. `/roundtable-save`
saves the current session or a specified list as a named preset. `/coach-list` now also
shows saved presets. The preset file is a plain JSON object, human-readable and
editable directly.

Design constraint honored: presets are stored in DATA_DIR (survives plugin updates),
not hardcoded anywhere in the plugin itself. The preset file is optional — if it doesn't
exist, `/roundtable` behavior is unchanged.

## Failure routes

- No yt-dlp → tell user the install command; web research carries the build.
- Zero captions (disabled/region) → web research carries the build, noted in the file.
- Ambiguous name → resolve to most prominent match, state the assumption in one line.
- No spoken media at all (historical) → writings-based persona in era register.

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

Explicitly out of scope: noticing/incorporating pre-existing files a user already has
sitting in a persona's folder before a build. That's a separate concern from this
plugin's own research pipeline — left to whatever's managing that folder externally
(e.g. a vault-sync skill), not duplicated here.

## Failure routes

- No yt-dlp → tell user the install command; web research carries the build.
- Zero captions (disabled/region) → web research carries the build, noted in the file.
- Ambiguous name → resolve to most prominent match, state the assumption in one line.
- No spoken media at all (historical) → writings-based persona in era register.

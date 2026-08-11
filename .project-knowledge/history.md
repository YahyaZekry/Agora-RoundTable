# History

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10
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

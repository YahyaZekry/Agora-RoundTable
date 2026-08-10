# History

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10
> Past-only. Append-only — never delete entries.

## Removed

*(none this session)*

---

## Fixed

*(none — no bugs; this session was feature work)*

---

## Decisions

- **Persist deep research per domain instead of discarding it into `persona.md`** — the
  template's 1,500-3,000-word budget is right for voice, but Step 4's web research was
  being distilled in and thrown away, with no way to go deeper than the summary later.
  Fix: `research/<domain>.md` (single domain) or `research/<domain>/` (multiple), plus
  a Deep-Dive Sources index in `persona.md` and a live-read instruction at embodiment
  time. Real gap confirmed by comparing against this repo's own bundled
  `examples/alex-hormozi/persona.md` and `examples/warren-buffett/persona.md` — dense,
  well-sourced examples that proved the *format* could hold real depth; the problem was
  research getting thrown away, not the format's ceiling. *(2026-08-10)*
- **Pre-existing-file scanning explicitly left out of scope** — noticing files a user
  already has in a persona folder before a build is a different concern
  (vault/folder-sync) from this plugin's own research pipeline. Not duplicated here.
  *(2026-08-10)*
- **Transcripts written as Markdown + frontmatter, not plain `.txt`** — `.md` renders
  properly and is self-descriptive (title, url, duration, view count, caption source,
  word count) when opened directly, not just parsed as raw input. *(2026-08-10)*

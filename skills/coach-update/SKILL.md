---
name: coach-update
description: Process any new files dropped into a coach's inbox/ folder and merge them into their research files. Does not rebuild the persona — use /coach-refresh for that.
argument-hint: [person's name]
disable-model-invocation: true
---

# /coach-update — sync inbox into research

The user wants to process new material in a coach's `inbox/` folder.

## Step 0 — Resolve DATA_DIR

Same as /coach Step 0:
1. `${CLAUDE_PLUGIN_DATA}/personas` if that substituted to a real absolute path
2. Otherwise fall back to `~/.claude/agora-roundtable/personas`

## Step 1 — Identify the coach

If `$ARGUMENTS` is provided, slugify it (same rule as /coach Step 1) and use that slug.
If `$ARGUMENTS` is empty, check `DATA_DIR/roundtable-session.json` for an active
roundtable, or a single-coach active session — if one is found, ask whether they mean
the current coach(es) or a different one. If nothing is active and no argument was
given, ask who to update.

Confirm `DATA_DIR/<slug>/persona.md` exists. If it doesn't, tell the user the coach
hasn't been built yet and to run `/coach <name>` first.

## Step 2 — Process inbox/

`DATA_DIR/<slug>/inbox/` is where the user drops their own files (notes, a dossier,
a PDF) to fold into this persona's research. Ensure the folder exists (create it,
empty, if missing).

Read `inbox/_sync-status.md` if it exists — a manifest table: file, last-synced date,
**coverage**, which `research/<domain-slug>.md` it was extracted into (PDFs can't hold
YAML frontmatter, so this manifest is the tracking mechanism). Treat any file with no
entry, modified after its logged date, **or logged as partial**, as needing extraction.
No manifest and no files in `inbox/`? Tell the user the inbox is empty and stop.

For each file needing extraction:
- Check `persona.md`'s Deep-Dive Sources for which domains already exist.
- **Text files:** read in full — don't delegate to a subagent and merge in its report;
  that's summary-of-a-summary loss. Extract real content — mechanisms, named
  frameworks, verbatim quotes, stories — and merge into the matching
  `research/<domain>.md`, genuinely integrated into its existing structure, not pasted
  as a raw dump. If nothing existing fits, create `research/<new-domain-slug>.md` and
  add it to `persona.md`'s Deep-Dive Sources.
- **PDFs:** read only the first 1-3 pages (a `pages` range — never the whole file).
  Extract what those pages show into the matching `research/<domain>.md`, labeled with
  the source and how many pages remain unread, so a later pass can continue with a
  `pages` range if needed.
- **Light touch only on `persona.md` itself:** pull at most a couple of the most
  distinctive new elements (a quote, a genuinely new framework name) into its
  compressed sections. The real depth belongs in `research/`, not duplicated into
  the summary.
- Update `inbox/_sync-status.md`: filename, today's date, coverage, which `research/`
  file(s) it went into. Create the manifest if this is its first entry.

**Coverage is a claim you have to be able to defend.** Before logging a file as
complete, walk its actual structure — headings, sections, chapters — and confirm each
one has a counterpart in `research/`. Anything you skipped, sampled, or read only part
of (every PDF, by definition) is logged as **partial**, naming what's left: "pages 1-3
of ~10 read," "concepts I, III-VI extracted; II and VII-XIII not yet." A partial
extraction logged as complete is worse than no entry at all.

## Step 2.5 — Close any gaps this material fills

If `DATA_DIR/<slug>/research/_gaps.md` exists, read its open entries. These are thin
spots found during actual use — by `/discuss` or `/coach-gaps` — and a `user-only` gap
is closed precisely by the user dropping the missing source into `inbox/`, which is
what just happened.

For each open entry, check whether the material extracted in Step 2 actually fills it.
If it does, mark it `Status: closed` with today's date. Never mark a gap closed on the
assumption that a dropped file *probably* covers it — confirm the content is now in
`research/`.

Mention closed gaps in the Step 3 report; that's the payoff for the user having gone
and found the source.

## Step 3 — Report and resume

When done, report what was synced: how many files, which `research/` files were
updated, any new domains created, and any `_gaps.md` entries this closed. If nothing
needed extraction, say so plainly ("inbox is clean — nothing new to sync").

If the updated coach is currently active in a session (check `roundtable-session.json`
or the coach context), tell the user the research files are updated and their next
question will draw on the new material automatically.

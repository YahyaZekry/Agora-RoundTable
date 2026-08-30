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
If `inbox/` is empty, say so in one line but **do not stop** — skip to Step 2.5, which
can still close `unmined` gaps from `transcripts/` without needing anything new.

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

## Step 2.5 — Close the gaps

If `DATA_DIR/<slug>/research/_gaps.md` exists, read its open entries. These are thin
spots found during actual use, by `/discuss` or `/coach-gaps`. **This command closes all
three kinds**, and never rebuilds anything to do it. Work through them cheapest first.

**a) `unmined` gaps — the material is already on disk.**

This is the free fix and it is the reason this step exists. An unmined gap means the
content sits in `transcripts/` (or in an `inbox/` file already logged as synced) but
never reached `research/`. No fetching, no web search, no new files from the user.

For each open `unmined` entry: go to `transcripts/` and read the parts that cover that
topic, then write the content into the matching `research/<domain>.md` directly. Same
rule as Step 2 — whoever reads the source writes the research file; do not summarize a
summary.

Do this even when `inbox/` is empty. An empty inbox is not a reason to skip the step,
and if you stop early here the user has no command that closes these at all short of a
full `/coach-refresh`, which is far more expensive and rebuilds things that were fine.

**b) `user-only` gaps — the user just supplied the missing source.**

These are closed precisely by a file landing in `inbox/`, which is what Step 2 just
processed. For each open entry, check whether the extracted material actually fills it.

**c) `unresearched` gaps — offer to research them, additively.**

These need a web search. Do not send the user to `/coach-refresh` for them: that command
rebuilds the whole cache to fix what is often one missing topic, and it throws away
transcripts and research that were perfectly good.

Instead, after (a) and (b), re-read `_gaps.md` and collect every entry still `open` (an
entry with no Status marker counts as open).

- **If none remain**, report "all gaps filled" and continue to Step 3.
- **If any remain**, stop and ask the user: *"N gaps are still open after the sync.
  Research them now?"* — and list them.
  - **If yes**, run the same research the original build used (`/coach` Steps 4 and 4.5:
    web research per gap, verified against sources), scoped to those gaps only. Write
    results into the matching `research/<domain>.md`, creating a new domain file if
    genuinely needed. Then mark what you filled.
  - **If no**, leave them open and name them in the report.

**This research pass is strictly additive.** Never delete or rebuild anything —
`persona.md`, `videos.json`, `transcripts/` and existing `research/` content are all
untouched. You are appending, not refreshing.

**Marking:** set `Status: closed` with today's date only after confirming the content is
now present in `research/`. Never close a gap on the assumption that a file *probably*
covered it.

Mention every closed gap in the Step 3 report.

## Step 3 — Report and resume

When done, report what was synced: how many files, which `research/` files were
updated, any new domains created, and any `_gaps.md` entries this closed. If nothing
needed extraction, say so plainly ("inbox is clean — nothing new to sync").

If the updated coach is currently active in a session (check `roundtable-session.json`
or the coach context), tell the user the research files are updated and their next
question will draw on the new material automatically.

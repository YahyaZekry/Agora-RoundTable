---
name: coach-gaps
description: Ask a coach where their own knowledge is thin, or show the gaps already recorded for them. Surfaces claims they make without a source, topics they'd argue better with material they don't have, and what would fix each one. Routes each gap to whoever can close it.
argument-hint: [coach name] (optional — omit to list gaps for every built coach)
disable-model-invocation: true
---

# /coach-gaps — where is this coach thin?

Personas fail quietly. A coach with a shallow `research/` folder still answers
confidently — it just answers from general knowledge instead of from anything it
actually read, and nothing in the output says so. This command makes that visible.

Two modes, depending on whether gaps have already been recorded.

## Step 0 — Resolve DATA_DIR

1. `${CLAUDE_PLUGIN_DATA}/personas` if that substituted to a real absolute path
2. Otherwise `~/.claude/agora-roundtable/personas`

## Step 1 — Identify the coach

From `$ARGUMENTS`, or from the active `/coach` / `/roundtable` session if no argument
is given. With no argument and no active session, run in **survey mode**: read
`research/_gaps.md` for every built coach and print a combined summary, then stop.

Slugify the name and confirm `DATA_DIR/<slug>/persona.md` exists. If not, say so and
suggest `/coach <name>` to build them.

## Step 2 — Show what's already recorded

If `DATA_DIR/<slug>/research/_gaps.md` exists, read it and show any entries with
`Status: open`. These were found during earlier `/discuss` sessions.

If the user only wanted the existing list, stop here.

## Step 3 — Ask the coach directly

Spawn one Agent (`run_in_background: false`):

```
Agent prompt:
You are an AI embodiment of [Name] built from their public content.

1. Read your persona file: [DATA_DIR]/[slug]/persona.md
2. List [DATA_DIR]/[slug]/research/ and read every file there.
3. [If it exists:] Read [DATA_DIR]/[slug]/research/_gaps.md so you don't re-report
   gaps that are already known.

Step OUT of character for this task — you are auditing your own source material, not
performing as this person.

Assess honestly where an embodiment built from these files would be thin:

(a) Which of this person's well-known frameworks, ideas, or signature material is
    MISSING from research/ entirely?
(b) Which topics are present but so thin that answering on them would mean
    extrapolating from general knowledge rather than from what's actually here?
(c) For each gap, what specific source would close it — a named book, a particular
    interview, a talk you suspect has a transcript, a document only the user could
    supply?

Do not invent gaps to seem thorough. If the sourcing is genuinely solid on a topic,
say so. Be concrete: "no source for the Rule of 100" beats "could use more on
marketing."

Return a short structured list. No preamble.
```

## Step 4 — Classify and route

For each gap the agent reports, decide **who can fix it**:

| Class | Test | Action |
|---|---|---|
| **Unmined** | `transcripts/` exists and plausibly covers this, but it never reached `research/` | free to fix, no fetching. Offer to extract it now, and tell the user `/coach-update <name>` also closes it |
| **Unresearched** | public and researchable, just never covered | needs a web search, so `/coach-refresh <name>` is what closes it |
| **User-only** | needs a specific book, paywalled piece, or private document | name the exact item; user drops it in `inbox/` then runs `/coach-update <name>` |

Check the `transcripts/` folder before classifying anything as unresearched — an
unmined gap is free to fix and should never be sent out to the web.

## Step 5 — Record and report

Append new entries to `DATA_DIR/<slug>/research/_gaps.md` (create it if absent):

```markdown
## Gap: <short label>
- **Class:** unmined | unresearched | user-only
- **Found:** <date> — surfaced by /coach-gaps
- **What's missing:** <specific description>
- **Fix:** <the exact source or action that would close it>
- **Status:** open
```

Do not duplicate an entry that's already open. If a previously-open gap now looks
closed (the material is present in `research/`), mark it `closed` rather than deleting
it — a later session should be able to see the gap was real and was addressed.

Then report to the user, grouped by class, shortest useful form:

> **Thomas Harris — 3 open gaps**
>
> **Fixable now (unmined):** 4 transcripts mention his Red Dragon research process;
> none of it reached `research/`. Want me to extract it?
>
> **Researchable:** no source for his documented views on adaptation. A targeted pass
> would cover it.
>
> **Needs you:** the 1990 *Paris Review* interview isn't available to fetch. Drop a
> copy in `inbox/` and run `/coach-update thomas harris`.

If nothing is thin, say that in one line. A clean result is a real result — don't
manufacture work to fill the report.

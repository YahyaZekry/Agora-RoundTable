---
name: coach-update-all
description: Process inbox/ and close known gaps for every built coach, or every coach in a named preset. Same as running /coach-update for each one individually.
argument-hint: (optional preset name — e.g. y-table)
disable-model-invocation: true
---

# /coach-update-all — sync inbox and close gaps for all coaches

## Step 0 — Resolve DATA_DIR

Same as /coach Step 0:
1. `${CLAUDE_PLUGIN_DATA}/personas` if that substituted to a real absolute path
2. Otherwise fall back to `~/.claude/agora-roundtable/personas`

## Step 1 — Build the target list

If `$ARGUMENTS` is a single token (no comma), slugify it and check
`DATA_DIR/roundtable-presets.json` for that key. If found, use only the coaches in
that preset. Say one line: **"Updating preset 'Y's Table': Thomas Harris, Joe Navarro."**

If `$ARGUMENTS` is empty, scan `DATA_DIR/` for every subdirectory that contains a
`persona.md`. That is the full target list. Say one line listing how many coaches were
found: **"Found 5 built coaches — checking inboxes."**

If no coaches are found at all, tell the user nothing is built yet and stop.

## Step 2 — Process each coach in sequence

For each coach, run **both** `/coach-update` Step 2 (inbox processing) **and Step 2.5
(gap closing)**. Do not stop at the inbox — a coach with an empty inbox may still have
open gaps that Step 2.5 can close for free from `transcripts/`.

- Check `DATA_DIR/<slug>/inbox/` for unsynced or partially-synced files
- Extract and merge into the appropriate `research/<domain>.md`
- Update `inbox/_sync-status.md`
- Read `research/_gaps.md`, close what can be closed, tidy the file

**One exception for the bulk case:** Step 2.5(c) normally stops to ask before doing web
research. Across many coaches that would mean many interruptions, so **do not ask
per-coach**. Collect every gap that would need research, skip them for now, and ask once
at the end (Step 3) covering all coaches together.

Label each coach clearly as you go:

```
**Thomas Harris** — 1 file synced, 2 gaps closed from transcripts
**Joe Navarro** — inbox clean, 1 gap closed, 1 needs research
```

## Step 3 — Summary

When all coaches are done, print a compact summary:

```
Update complete — 5 coaches checked.
  Synced: Thomas Harris (1 file), Gillian Flynn (2 files)
  Gaps closed: 4 across 3 coaches
  Clean: Joe Navarro, Dennis Lehane
```

Then, if any gaps were skipped because they need web research, ask once for all of them:
*"6 gaps across 3 coaches need web research. Do them now?"* — and list them grouped by
coach. If yes, research them scoped to those gaps only, strictly additive. If no, leave
them open.

If nothing was synced and no gaps were open anywhere, say so plainly: **"All inboxes
clean, no open gaps."**

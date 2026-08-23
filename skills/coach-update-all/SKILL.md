---
name: coach-update-all
description: Process inbox/ for every built coach, or every coach in a named preset. Same as running /coach-update for each one individually.
argument-hint: (optional preset name — e.g. y-table)
disable-model-invocation: true
---

# /coach-update-all — sync inbox for all coaches

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

For each coach in the target list, run the full inbox processing logic from
`/coach-update` Step 2:

- Check `DATA_DIR/<slug>/inbox/` for unsynced or partially-synced files
- Extract and merge into the appropriate `research/<domain>.md`
- Update `inbox/_sync-status.md`

Label each coach clearly as you go:

```
**Thomas Harris** — 1 new file synced (notes-on-will-graham.md → research/empathy-profiling.md)
**Joe Navarro** — inbox clean, nothing to sync
```

## Step 3 — Summary

When all coaches are done, print a compact summary:

```
Inbox sync complete — 5 coaches checked.
  Synced: Thomas Harris (1 file), Gillian Flynn (2 files)
  Clean: Joe Navarro, Dennis Lehane, David Simon
```

If nothing was synced anywhere, say so plainly: **"All inboxes clean — nothing to sync."**

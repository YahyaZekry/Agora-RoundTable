---
name: coach-refresh-all
description: Rebuild every built coach from fresh research, or every coach in a named preset. Same as running /coach-refresh for each one individually. This is slow — it pulls new transcripts and does full web research per coach.
argument-hint: (optional preset name — e.g. y-table)
disable-model-invocation: true
---

# /coach-refresh-all — full rebuild for all coaches

This is the slow operation. Each coach gets new transcripts pulled, fresh web research
per domain, a verification pass, a new persona.md, and inbox sync. Expect several
minutes per coach.

## Step 0 — Resolve DATA_DIR

Same as /coach Step 0:
1. `${CLAUDE_PLUGIN_DATA}/personas` if that substituted to a real absolute path
2. Otherwise fall back to `~/.claude/agora-roundtable/personas`

## Step 1 — Build the target list

If `$ARGUMENTS` is a single token (no comma), slugify it and check
`DATA_DIR/roundtable-presets.json` for that key. If found, use only the coaches in
that preset. Say: **"Rebuilding preset 'Y's Table': Thomas Harris, Joe Navarro. This
will take several minutes."**

If `$ARGUMENTS` is empty, scan `DATA_DIR/` for every subdirectory that contains a
`persona.md`. Say: **"Rebuilding N coaches — this will take a while. Coaches are
rebuilt one at a time."**

If no coaches are found, tell the user nothing is built yet and stop.

**Warn before starting:** rebuilding replaces all transcripts, research files, and
persona.md for each coach. The user's own `inbox/` files are NOT deleted — they'll be
re-extracted into the fresh research. Confirm with one line: **"Starting rebuild. inbox/
files are safe."**

## Step 2 — Rebuild each coach in sequence

For each coach in the target list, run the full `/coach-refresh` pipeline:

1. Delete `persona.md`, `videos.json`, `transcripts/`, `research/` contents, and
   `inbox/_sync-status.md` (not `inbox/` itself — user files are preserved)
2. Run the full `/coach` build from Step 1 (fetch transcripts, deep web research,
   verify, distill into persona.md)
3. Run `/coach-update` inbox sync for this coach

Label each coach as you go:

```
**Rebuilding Thomas Harris** (1 of 2)...
  ✅ Thomas Harris rebuilt — 8 transcripts, 3 research domains, inbox synced.

**Rebuilding Joe Navarro** (2 of 2)...
  ✅ Joe Navarro rebuilt — 6 transcripts, 2 research domains, inbox clean.
```

## Step 3 — Summary

When all coaches are done:

```
Rebuild complete — 2 coaches refreshed.
  Thomas Harris — 8 transcripts, 3 domains, 1 inbox file synced
  Joe Navarro   — 6 transcripts, 2 domains, inbox clean
```

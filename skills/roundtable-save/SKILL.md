---
name: roundtable-save
description: Save the current roundtable as a named preset, or define a new preset from a list of coaches. Run /roundtable <preset-name> to load it later.
argument-hint: <preset-name> [coach1, coach2, ...]
disable-model-invocation: true
---

# /roundtable-save — save a named roundtable preset

The user wants to save a preset named: **$ARGUMENTS**

## Step 0 — Resolve DATA_DIR

Same as /coach Step 0:
1. `${CLAUDE_PLUGIN_DATA}/personas` if that substituted to a real absolute path
2. Otherwise fall back to `~/.claude/agora-roundtable/personas`

Presets file: `DATA_DIR/roundtable-presets.json`

## Step 1 — Parse the arguments

Split $ARGUMENTS on the first space or comma to separate the preset name from the coaches list.

**Form A — name only** (e.g. `/roundtable-save y-table`):
- No coaches listed → use the active `roundtable-session.json` as the source.
- If no session is active, tell the user to either start a roundtable first or provide
  coach names: `/roundtable-save y-table thomas harris, joe navarro`.

**Form B — name + coaches** (e.g. `/roundtable-save y-table thomas harris, joe navarro`):
- Parse everything after the first space/comma-group as a comma-separated coach list.
- Slugify each coach name.
- Verify each `DATA_DIR/<slug>/persona.md` exists. List any that don't — they can still
  be added to the preset, but warn that they'll fail if `/roundtable y-table` is run
  before those coaches are built.

## Step 2 — Slugify the preset name

Lowercase, replace spaces with hyphens: "Y's Table" → `y-table`, "charlotte table" → `charlotte-table`.

## Step 3 — Read and update presets file

If `DATA_DIR/roundtable-presets.json` exists, read it. Otherwise start with `{}`.

Add or overwrite the entry:
```json
{
  "<preset-slug>": {
    "display": "<original name as given, title-cased>",
    "coaches": ["<slug1>", "<slug2>", ...]
  }
}
```

Write the file back.

## Step 4 — Confirm

Print one confirmation block:

> **Preset saved: "Y's Table"**
> Coaches: Thomas Harris, Joe Navarro
> Run `/roundtable y-table` to load it.
>
> _[If any coaches weren't built yet: ⚠ thomas-harris not yet built — run `/coach thomas harris` first.]_

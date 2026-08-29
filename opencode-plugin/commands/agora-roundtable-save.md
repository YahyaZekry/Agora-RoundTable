---
description: Save the active roundtable as a named preset, or define one from a list of coaches.
agent: agora-facilitator
subtask: true
---
Save a named roundtable preset from $ARGUMENTS — form "PRESET-NAME" (use active roundtable-session.json) or "PRESET-NAME coach1, coach2". Resolve the shared data dir. Slugify the preset name and the coaches. Verify each coach's persona exists (warn for any that don't, but still allow saving). Read/write roundtable-presets.json — the entry is { "<preset-slug>": { "display": "<name>", "coaches": ["<slug1>", ...] } }. Confirm the saved preset and how to load it.

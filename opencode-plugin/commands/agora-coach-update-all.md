---
description: Sync inbox/ and close known gaps for every built coach, or every coach in a named preset.
agent: agora-facilitator
subtask: true
---
Run the full coach-update flow — inbox sync AND gap closing — for every built coach, or if $ARGUMENTS is a single token matching a preset in roundtable-presets.json, only that preset's coaches.

Do not stop at the inbox: a coach with an empty inbox may still have open gaps that can be closed for free from transcripts/. For each coach, process inbox/ then read research/_gaps.md and close what can be closed without the web, tidying the file afterwards.

One exception for the bulk case: coach-update normally stops to ask before doing web research on remaining gaps. Across many coaches that means many interruptions, so do NOT ask per-coach — collect every gap needing research, skip them, and ask once at the end covering all coaches together. If the user agrees, research them scoped to those gaps only, strictly additive.

Label each coach as you go and print a compact summary at the end covering files synced, gaps closed, and anything still needing research.

---
description: Rebuild every built coach from fresh research, or every coach in a named preset.
agent: agora-facilitator
subtask: true
---
Rebuild every built coach (or, if $ARGUMENTS is a single token that matches a preset in roundtable-presets.json, only that preset's coaches). Resolve the shared data dir and build the target list. Warn that this is slow (roughly several minutes per coach) and that the user's inbox/ files are safe. For each coach, run the full coach-refresh pipeline: wipe the cache, rebuild persona from Step 1, sync inbox. Label each coach as you go and print a compact summary at the end.

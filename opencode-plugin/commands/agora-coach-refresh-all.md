---
description: Rebuild every built coach from fresh research, or every coach in a named preset.
agent: agora-facilitator
subtask: true
---
Rebuild every built coach (or, if $ARGUMENTS is a single token that matches a preset in roundtable-presets.json, only that preset's coaches). Resolve the shared data dir and build the target list. Warn that this is slow (roughly several minutes per coach) and that the user's inbox/ files are safe. For each coach, run the full coach-refresh pipeline exactly as that command defines it — including moving the old cache to .refresh-backup/ rather than deleting it, verifying the rebuild, and restoring the backup if the build fails. Never delete a persona's cache outright. Then sync inbox and close gaps per coach-update. Label each coach as you go and print a compact summary at the end.

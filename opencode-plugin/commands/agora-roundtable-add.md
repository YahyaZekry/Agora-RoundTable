---
description: Add a coach to an active roundtable session.
agent: agora-facilitator
subtask: true
---
Add the coach in $ARGUMENTS to the active roundtable. Read roundtable-session.json (if missing, say no roundtable is active and that /agora roundtable <names> starts one). If $ARGUMENTS is empty, ask who to add. Slugify, verify the persona exists (else tell them to /agora coach it first), check it's not already in the room, add it, save, and confirm the full active list. Continue facilitating in roundtable mode.

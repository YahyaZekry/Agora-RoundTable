---
name: roundtable-add
description: Add a coach to an active roundtable session mid-conversation.
argument-hint: [person's name]
disable-model-invocation: true
---

# /roundtable-add — add a coach to the room

The user wants to add **$ARGUMENTS** to the current roundtable.

1. Resolve DATA_DIR same as /coach Step 0.
2. Read `DATA_DIR/roundtable-session.json`. If it doesn't exist, no roundtable is
   active — tell the user to start one with `/roundtable <names>`.
3. If `$ARGUMENTS` is empty, ask who to add.
4. Slugify the name. Check if `DATA_DIR/<slug>/persona.md` exists. If not, tell the
   user to build it first with `/coach <name>` and come back.
5. Check if the coach is already in the session. If so, say so and stop.
6. Add `{ "slug": "<slug>", "name": "<display name>" }` to the coaches array and
   save `roundtable-session.json`.
7. Confirm in one line: "[Name] joined the roundtable. Active: [full list]."
8. Continue facilitating in roundtable mode — the new coach is now in the room for
   all subsequent messages.

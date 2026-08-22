---
name: roundtable-remove
description: Remove a coach from an active roundtable session mid-conversation.
argument-hint: [person's name]
disable-model-invocation: true
---

# /roundtable-remove — remove a coach from the room

The user wants to remove **$ARGUMENTS** from the current roundtable.

1. Resolve DATA_DIR same as /coach Step 0.
2. Read `DATA_DIR/roundtable-session.json`. If it doesn't exist, say no roundtable
   is active.
3. If `$ARGUMENTS` is empty, ask who to remove.
4. Find the matching coach (fuzzy match on name or slug). If no match, say so and
   list the active coaches.
5. Remove them from the coaches array and save `roundtable-session.json`.
6. If only one coach remains, ask the user: "Only [Name] is left — continue as a
   roundtable or switch to `/coach [name]`?" Wait for their answer before proceeding.
7. If two or more remain, confirm in one line: "[Name] left the roundtable.
   Active: [remaining list]."
8. Continue facilitating with the updated roster.

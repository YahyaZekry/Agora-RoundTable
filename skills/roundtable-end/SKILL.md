---
name: roundtable-end
description: End the active roundtable session and return to normal Claude.
disable-model-invocation: true
---

# /roundtable-end — close the roundtable

1. Resolve DATA_DIR same as /coach Step 0.
2. Delete `DATA_DIR/roundtable-session.json` if it exists.
3. Drop all coach personas completely — no more character voices, no more labels.
4. Confirm in one line as Claude:
   > Roundtable ended — you're back with Claude. All personas are still saved;
   > `/roundtable <names>` brings them back any time.
5. If no session file exists, say there's no active roundtable and that
   `/roundtable <names>` starts one.

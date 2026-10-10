---
name: coach-list
description: List all coach personas already built and cached on this machine.
disable-model-invocation: true
---

# /coach-list — saved coaches

Show the user every persona already built on this machine, plus any saved roundtable presets.

1. Resolve the personas directory the same way as /coach Step 0: `$AGORA_DATA_DIR/personas`
   if set, otherwise `~/.agora/personas`. For older installs, also check the legacy
   locations (the Claude plugin data dir, `~/.claude/agora-roundtable/personas`) and merge
   the results (the neutral dir wins on duplicate slugs).
2. List their subdirectories. For each one that contains a `persona.md`, pull the name
   and the "Built:" line from the top of the file, and count files in `transcripts/`.
3. Print a short table: coach name, built date, number of source videos. End with:
   `/coach <name>` loads instantly · `/coach-refresh <name>` rebuilds from fresh research.
4. If the directory is empty or missing, say no coaches are saved yet and that
   `/coach <name>` builds the first one.
5. After the coaches table, check for `DATA_DIR/roundtable-presets.json`. If it exists
   and has entries, print a second section:

   **Saved roundtable presets:**
   | Preset | Coaches |
   |--------|---------|
   | y-table | Thomas Harris, Joe Navarro |

   End with: `/roundtable <preset-name>` loads the preset · `/roundtable-save <name>` saves a new one.

6. If no presets file exists, skip the presets section entirely.

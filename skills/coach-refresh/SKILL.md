---
name: coach-refresh
description: Rebuild a cached coach persona from fresh research — new videos, updated frameworks.
argument-hint: [person's name]
disable-model-invocation: true
---

# /coach-refresh — rebuild a persona

The user wants **$ARGUMENTS** rebuilt from scratch (their content has moved on, or the
first build was thin). If `$ARGUMENTS` is empty, ask who to refresh.

1. Resolve the personas directories the same way as /coach Step 0
   (`${CLAUDE_PLUGIN_DATA}/personas` primary, `~/.claude/agora-roundtable/personas`
   legacy fallback) and the person's slug.
2. **Read `<personas>/<slug>/research/_gaps.md` if it exists** and keep its open
   entries in mind. Those are known thin spots found by `/discuss` or `/coach-gaps`
   during actual use, and they turn this from a generic rebuild into a targeted one.
   This file survives the rebuild.
3. **Move the old cache aside. Never delete it before the rebuild succeeds.**

   A persona folder is often a symlink into the user's notes vault. Deleting first and
   rebuilding second means any failure — an API error, a failed search, the user
   interrupting — destroys work with no undo. So move, don't delete:

   ```bash
   BACKUP="<personas>/<slug>/.refresh-backup"
   mkdir -p "$BACKUP"
   mv "<personas>/<slug>/persona.md"    "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/videos.json"   "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/transcripts"   "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/research"      "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/inbox/_sync-status.md" "$BACKUP/" 2>/dev/null
   mkdir -p "<personas>/<slug>/research" "<personas>/<slug>/transcripts"
   ```

   Then restore `_gaps.md` immediately, since the rebuild needs it:
   ```bash
   cp "$BACKUP/research/_gaps.md" "<personas>/<slug>/research/" 2>/dev/null
   ```

   Never touch the rest of `inbox/` — those are the user's own dropped files, not cache.

4. Run the full `/coach` build for the name: read
   `${CLAUDE_PLUGIN_ROOT}/skills/coach/SKILL.md` and follow it from Step 1 (the cache
   check will miss, forcing fresh research and transcript pulls). **Give the open
   `_gaps.md` entries priority during Step 4's research** — an unmined gap means the
   content is already in `transcripts/` and just needs extracting; an unresearched gap
   means that topic needs a dedicated search rather than being folded into a general
   pass.

   **If the fetcher returns zero transcripts but the backup has some**, restore them
   rather than proceeding with none — videos get deleted, region-blocked, or have
   captions turned off, and a transcript you already have is worth more than a fresh
   empty fetch:
   ```bash
   cp -r "$BACKUP/transcripts/." "<personas>/<slug>/transcripts/" 2>/dev/null
   ```

4.5. **Verify the rebuild before discarding the backup.** Confirm
   `<personas>/<slug>/persona.md` exists and is non-trivial (a real persona file, not a
   stub or an error message), and that `research/` has at least one domain file.

   - **If it succeeded**, delete the backup: `rm -rf "$BACKUP"`. Say in one line that
     the old cache was replaced.
   - **If it failed for any reason**, restore everything and stop. Do not leave the user
     with a half-built persona:
     ```bash
     mv "$BACKUP"/* "<personas>/<slug>/" 2>/dev/null
     rmdir "$BACKUP"
     ```
     Then tell the user plainly what failed and that the original persona is intact.
5. After the build completes, run `/coach-update` for this coach: read
   `${CLAUDE_PLUGIN_ROOT}/skills/coach-update/SKILL.md` and follow its Step 2 to
   re-extract everything currently in `inbox/` into the freshly rebuilt `research/`.
6. **Reconcile `_gaps.md`** — for each open entry, check whether the rebuild actually
   closed it. Mark closed ones `Status: closed` with the date; leave genuinely
   unclosed ones open. Never mark a gap closed without confirming the material is
   present in `research/`. Report in one line how many closed and how many remain.
7. Finish by adopting the rebuilt persona per /coach Step 6, and note in the handoff
   line that it was rebuilt fresh — and whether any gaps are still open.

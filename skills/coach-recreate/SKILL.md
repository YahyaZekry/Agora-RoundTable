---
name: coach-recreate
description: Delete and rebuild a coach from scratch from fresh research (new videos, updated frameworks). The old persona, transcripts and research are replaced; the old build is kept aside until the new one succeeds and restored if it fails. Files in inbox/ are never touched.
argument-hint: [person's name]
disable-model-invocation: false
---

# /coach-recreate — delete and rebuild a persona from scratch

The user wants **$ARGUMENTS** deleted and rebuilt from scratch (their content has moved on,
or the first build was thin). If `$ARGUMENTS` is empty, follow step 0.

**Replaced:** `persona.md`, `videos.json`, `transcripts/` and `research/` are thrown away and
rebuilt, including any research file the user edited by hand. **Kept:** everything the user
dropped in `inbox/` (re-extracted into the new research afterwards) and `research/_gaps.md`.
The old build is kept aside until the new one passes its checks, and restored if the rebuild
fails. If the user only wants to add material or fill gaps, send them to `/coach-update`
instead: it never throws anything away.

0. **Which coach?** Decide this before doing anything else.
   - A name in `$ARGUMENTS` → that coach.
   - No name, and one coach is active in THIS conversation (adopted by `/coach` or
     `/coach-switch`, not ended since) → that coach. Start the reply by naming them:
     "Recreating **<Full Name>** (your active coach)." Then continue.
   - No name, and several coaches are active (a roundtable) → ask which one, listing them.
   - No name and no active coach (a new chat, or after `/coach-end`) → ask "Which coach do you
     want to recreate?" and list the built coaches (every folder in the personas directory
     with a `persona.md`). Do nothing until they answer.
   Decide from this conversation only: never from `roundtable-session.json` or memory of an
   earlier chat, and never recreate more than one coach per command.

1. Resolve the personas directory the same way as /coach Step 0
   (`$AGORA_DATA_DIR/personas` if set, otherwise `~/.agora/personas`) and the person's slug.
2. **Read `<personas>/<slug>/research/_gaps.md` if it exists** and keep its open
   entries in mind. Those are known thin spots found by `/discuss` or `/coach-gaps`
   during actual use, and they turn this from a generic rebuild into a targeted one.
   This file survives the rebuild. Also note the overall score in
   `<personas>/<slug>/coach-health.json` if it exists; the new build is compared against it
   at the end.
3. **Move the old cache aside. Never delete it before the rebuild succeeds.**

   A persona folder is often a symlink into the user's notes vault. Deleting first and
   rebuilding second means any failure — an API error, a failed search, the user
   interrupting — destroys work with no undo. So move, don't delete:

   ```bash
   BACKUP="<personas>/<slug>/.recreate-backup"
   mkdir -p "$BACKUP"
   mv "<personas>/<slug>/persona.md"    "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/videos.json"   "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/transcripts"   "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/research"      "$BACKUP/" 2>/dev/null
   mv "<personas>/<slug>/inbox/_sync-status.md" "$BACKUP/" 2>/dev/null
   mkdir -p "<personas>/<slug>/research" "<personas>/<slug>/transcripts"
   ```

   If a `.refresh-backup` folder exists (left by an interrupted run from before this
   command was renamed from `/coach-refresh`), restore it first:
   `mv "<personas>/<slug>/.refresh-backup"/* "<personas>/<slug>/" && rmdir "<personas>/<slug>/.refresh-backup"`.

   Then restore `_gaps.md` immediately, since the rebuild needs it:
   ```bash
   cp "$BACKUP/research/_gaps.md" "<personas>/<slug>/research/" 2>/dev/null
   ```

   Never touch the rest of `inbox/` — those are the user's own dropped files, not cache.

4. Run the full `/coach` build for the name: read
   the `coach` skill in this same plugin and follow it from Step 1 (the cache
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

   - **If it succeeded**, run `python3 "$PLUGIN_ROOT/scripts/coach_health.py" "<personas>/<slug>"`
     and compare with the old score from step 2. If the new overall score is more than 10
     points LOWER, keep the backup, say so plainly (old score, new score, why), and ask the
     user whether to keep the new build or restore the old one. Otherwise delete the backup:
     `rm -rf "$BACKUP"`, and say in one line that the old build was replaced, with old → new
     score.
   - **If it failed for any reason**, restore everything and stop. Do not leave the user
     with a half-built persona:
     ```bash
     mv "$BACKUP"/* "<personas>/<slug>/" 2>/dev/null
     rmdir "$BACKUP"
     ```
     Then tell the user plainly what failed and that the original persona is intact.
5. After the build completes, run `/coach-update` for this coach: read
   the `coach-update` skill in this same plugin and follow its Step 2 to
   re-extract everything currently in `inbox/` into the freshly rebuilt `research/`.
6. **Reconcile `_gaps.md`** — for each open entry, check whether the rebuild actually
   closed it. Mark closed ones `Status: closed` with the date; leave genuinely
   unclosed ones open. Never mark a gap closed without confirming the material is
   present in `research/`. Report in one line how many closed and how many remain.
7. Finish by adopting the rebuilt persona per /coach Step 6, and note in the handoff
   line that it was rebuilt fresh — and whether any gaps are still open.

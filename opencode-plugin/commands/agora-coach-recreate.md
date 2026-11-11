---
description: Delete and rebuild a coach from scratch from fresh research (old build kept aside until the new one succeeds).
agent: agora-facilitator
subtask: true
---
Delete and rebuild a persona from scratch. First decide which coach: a name in $ARGUMENTS means that coach. With no name and one coach active in THIS conversation (adopted by coach or coach-switch, not ended since), use that coach and start the reply by naming them ("Recreating <Full Name> (your active coach)."). With no name and several coaches active, ask which one, listing them. With no name and no active coach (a new chat, or after coach-end), ask "Which coach do you want to recreate?" and list the built coaches (every folder in the personas dir with a persona.md); do nothing until they answer. Decide from this conversation only, never from roundtable-session.json or an earlier chat, and never recreate more than one coach per command. Then resolve the shared data dir. Replaced: persona.md, videos.json, transcripts/ and research/ (including any research file the user edited by hand). Kept: everything in inbox/ (re-extracted afterwards) and research/_gaps.md. If the user only wants to add material or fill gaps, send them to coach-update, which never throws anything away. Also note the overall score in PERSONAS/<slug>/coach-health.json if it exists.

First, read PERSONAS/<slug>/research/_gaps.md and keep open entries in mind — they are known thin spots to target during the rebuild.

**Never delete the cache before the rebuild succeeds.** A persona folder is often a symlink into the user's notes vault, so deleting first and rebuilding second means any failure (API error, failed search, user interrupt) destroys real work with no undo. Move it aside instead:

```bash
BACKUP="PERSONAS/<slug>/.recreate-backup"
mkdir -p "$BACKUP"
mv "PERSONAS/<slug>/persona.md"  "$BACKUP/" 2>/dev/null
mv "PERSONAS/<slug>/videos.json" "$BACKUP/" 2>/dev/null
mv "PERSONAS/<slug>/transcripts" "$BACKUP/" 2>/dev/null
mv "PERSONAS/<slug>/research"    "$BACKUP/" 2>/dev/null
mv "PERSONAS/<slug>/inbox/_sync-status.md" "$BACKUP/" 2>/dev/null
mkdir -p "PERSONAS/<slug>/research" "PERSONAS/<slug>/transcripts"
cp "$BACKUP/research/_gaps.md" "PERSONAS/<slug>/research/" 2>/dev/null
```

Never touch the rest of inbox/ — those are the user's own files, not cache.

Then run the full coach build from Step 1, giving open _gaps.md entries priority during research. If the fetcher returns zero transcripts but the backup has some, restore them (`cp -r "$BACKUP/transcripts/." "PERSONAS/<slug>/transcripts/"`) rather than proceeding with none — videos get deleted or region-blocked, and transcripts you already have beat a fresh empty fetch.

**Verify before discarding the backup.** Confirm persona.md exists and is a real persona file (not a stub or an error), and that research/ has at least one domain file. If it succeeded, run `python3 <repo>/scripts/coach_health.py "PERSONAS/<slug>"` and compare with the old score: if the new overall score is more than 10 points LOWER, keep the backup, say so plainly, and ask whether to keep the new build or restore the old one; otherwise `rm -rf "$BACKUP"` and report old → new score. If a `.refresh-backup` folder exists from before the rename from coach-refresh, restore it first. If it failed for any reason, restore everything (`mv "$BACKUP"/* "PERSONAS/<slug>/"; rmdir "$BACKUP"`), tell the user what failed, and confirm the original persona is intact. Never leave a half-built persona.

After a successful build, run the coach-update inbox sync (see the coach-update skill), reconcile _gaps.md (set Status: closed for entries the rebuild filled, per the gap-tracking convention in the agora-coach skill), and re-adopt the persona.

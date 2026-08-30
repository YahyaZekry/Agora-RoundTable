---
description: Rebuild a cached coach persona from fresh research.
agent: agora-facilitator
subtask: true
---
Rebuild the persona for $ARGUMENTS from scratch. Resolve the shared data dir.

First, read PERSONAS/<slug>/research/_gaps.md and keep open entries in mind — they are known thin spots to target during the rebuild.

**Never delete the cache before the rebuild succeeds.** A persona folder is often a symlink into the user's notes vault, so deleting first and rebuilding second means any failure (API error, failed search, user interrupt) destroys real work with no undo. Move it aside instead:

```bash
BACKUP="PERSONAS/<slug>/.refresh-backup"
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

**Verify before discarding the backup.** Confirm persona.md exists and is a real persona file (not a stub or an error), and that research/ has at least one domain file. If it succeeded, `rm -rf "$BACKUP"`. If it failed for any reason, restore everything (`mv "$BACKUP"/* "PERSONAS/<slug>/"; rmdir "$BACKUP"`), tell the user what failed, and confirm the original persona is intact. Never leave a half-built persona.

After a successful build, run the coach-update inbox sync (see the coach-update skill), reconcile _gaps.md (set Status: closed for entries the rebuild filled, per the gap-tracking convention in the agora-coach skill), and re-adopt the persona.

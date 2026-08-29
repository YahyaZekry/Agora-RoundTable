---
description: Rebuild a cached coach persona from fresh research.
agent: agora-facilitator
subtask: true
---
Rebuild the persona for $ARGUMENTS from scratch. Resolve the shared data dir. Before deleting anything, read PERSONAS/<slug>/research/_gaps.md and keep open entries in mind (they are known thin spots to target). Delete only the cache: persona.md, videos.json, transcripts/, research/ contents (except _gaps.md), and inbox/_sync-status.md — leave the rest of inbox/ (user files). Then run the full coach build from Step 1, giving open _gaps.md entries priority during research. After the build, run the coach-update inbox sync (see the coach-update skill), reconcile _gaps.md (mark closed ones), and re-adopt the persona.

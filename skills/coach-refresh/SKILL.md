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
2. **Before deleting anything, read `<personas>/<slug>/research/_gaps.md` if it
   exists** and keep its open entries in mind — those are known thin spots found by
   `/discuss` or `/coach-gaps` during actual use. They turn this from a generic
   rebuild into a targeted one. Preserve this file through the wipe.
3. Wherever `<personas>/<slug>/` exists (check both locations), delete only its
   `persona.md`, `videos.json`, `transcripts/` contents, `research/` contents **except
   `_gaps.md`**, and `inbox/_sync-status.md` (not the rest of `inbox/` — those are the
   user's dropped files, not cache; deleting just the manifest forces re-extraction of
   all of them into the freshly rebuilt `research/`). That's the entire cache for this
   person. Leave every other file untouched — it isn't plugin-owned.
4. Run the full `/coach` build for the name: read
   `${CLAUDE_PLUGIN_ROOT}/skills/coach/SKILL.md` and follow it from Step 1 (the cache
   check will miss, forcing fresh research and transcript pulls). **Give the open
   `_gaps.md` entries priority during Step 4's research** — an unmined gap means the
   content is already in `transcripts/` and just needs extracting; an unresearched gap
   means that topic needs a dedicated search rather than being folded into a general
   pass.
5. After the build completes, run `/coach-update` for this coach: read
   `${CLAUDE_PLUGIN_ROOT}/skills/coach-update/SKILL.md` and follow its Step 2 to
   re-extract everything currently in `inbox/` into the freshly rebuilt `research/`.
6. **Reconcile `_gaps.md`** — for each open entry, check whether the rebuild actually
   closed it. Mark closed ones `Status: closed` with the date; leave genuinely
   unclosed ones open. Never mark a gap closed without confirming the material is
   present in `research/`. Report in one line how many closed and how many remain.
7. Finish by adopting the rebuilt persona per /coach Step 6, and note in the handoff
   line that it was rebuilt fresh — and whether any gaps are still open.

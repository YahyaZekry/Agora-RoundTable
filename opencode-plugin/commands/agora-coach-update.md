---
description: Sync new files the user dropped into a coach's inbox/ into their research files, then close every gap that can be closed.
agent: agora-facilitator
subtask: true
---
Resolve the shared data dir, identify the coach ($ARGUMENTS, or ask if empty), confirm the persona exists.

**1. Process inbox/.** Read inbox/_sync-status.md and extract any file with no entry, modified after its logged date, or logged partial — merge into matching research/<domain>.md (or create a new domain). For PDFs, read only the first 1-3 pages and log coverage as partial. An empty inbox is NOT a reason to stop: say so in one line and carry on to the gap work, which can still close gaps without anything new. inbox/ belongs to the user — read from it, never write into it (the sole exception is _sync-status.md), and never delete or modify a file after extracting it. Some files there are questions rather than sources: a note asking the user to decide something has nothing to mine, so log it as a pending decision, surface the question, and do not invent an answer.

**2. Read research/_gaps.md.** It comes in two shapes and you must handle both: structured `## Gap:` blocks carrying `Status:`, or free-form prose under `### Unmined` / `### Unresearched` / `### User-only` headings with no Status markers at all (what post-debate audits actually produce). In the second shape treat every bullet as open. Never report "all gaps filled" just because no Status marker was found. If the file does not exist there are no known gaps — report the sync and stop.

**3. Close `unmined` gaps first — they are free.** Unmined covers two cases: content in transcripts/ that never reached research/, or content in research/ that never surfaced into persona.md. Historical figures have no transcripts, so for them every unmined gap is the second kind — pull it up into persona.md in that file's compressed style, not wholesale. An empty transcripts/ folder does not mean there are no unmined gaps. No fetching, no web search. Whoever reads the source writes the destination — never summarize a summary.

**4. Close `user-only` gaps** that the files just synced from inbox/ actually fill. Confirm the content is really in research/ before marking anything closed — never close on the assumption that a dropped file probably covered it.

**5. Offer to research whatever is left.** Re-collect the still-open entries. If none remain, report "all gaps filled". If any remain, STOP and ask with the question tool: "N gaps are still open after the sync — research them now using the same tools that built <coach> the first time?" (list them). If yes, run the build's research workflow (agora-coach skill Steps 1–5: web research and primary-source reading, written into the appropriate research/<domain>.md, creating new domain files when needed) scoped to those gaps only. If no, leave them open and report them.

This research pass is strictly additive — never delete or rebuild the cache (persona.md, videos.json, transcripts/, or research/ except as appended to).

**6. Tidy the gaps file.** Recount after all marking is done. If nothing is open any more, DELETE research/_gaps.md entirely — an empty gaps file is clutter and implies gaps that no longer exist — and say so in one line. If some are still open, keep it and put a single status line at the very top: `<!-- N open, M closed — last checked YYYY-MM-DD -->`. One line, starting with the counts, updated in place — never a second one, and nothing beyond the counts and the date (detail belongs in the entries). Both runtimes must write this identically.

Report what was synced, which gaps closed, and what is still open.

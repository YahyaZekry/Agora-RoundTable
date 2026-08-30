---
description: Sync new files the user dropped into a coach's inbox/ into their research files, then offer to research whatever gaps remain.
agent: agora-facilitator
subtask: true
---
Process new material in a coach's inbox/ folder and merge it into their research files. Resolve the shared data dir, identify the coach ($ARGUMENTS, or ask if empty), confirm the persona exists. Read inbox/_sync-status.md and extract any file with no entry, modified after its logged date, or logged partial — merge into matching research/<domain>.md (or create a new domain). For PDFs, read only the first 1-3 pages and log coverage as partial. Then close any _gaps.md entries the new material fills (set their Status to `closed` and note the source file).

An empty inbox is NOT a reason to stop — say so in one line and carry on to the gap work below, which can still close gaps without anything new.

Before considering any web research, close the free ones: for every open `unmined` gap (content already sitting in transcripts/ that never reached research/), read the relevant parts of transcripts/ and write them into the matching research/<domain>.md directly. No fetching, no web search. Whoever reads the source writes the research file — never summarize a summary.

Report what was synced; say plainly if the inbox is clean.

After syncing, re-read research/_gaps.md and collect every entry whose Status is still `open` (an absent Status marker counts as open). If none remain, report "all gaps filled" and stop. If open entries remain, STOP and ask the user with the question tool: "N gaps are still open after the inbox sync — research them now using the same tools that built <coach> the first time?" (list the open gaps). If the user says yes, run the original build research workflow (agora-coach skill Steps 1–5: web research / primary-source reading, writing results into the appropriate research/<domain>.md, creating new domain files when needed) scoped to those outstanding gaps only, then reconcile _gaps.md (set Status: closed where filled). If the user says no, leave the gaps open and report them. This research pass is strictly additive — never delete or rebuild the cache (persona.md, videos.json, transcripts/, or research/ except as appended/updated).

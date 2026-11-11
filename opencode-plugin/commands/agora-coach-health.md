---
description: Show a coach's deterministic health score (no AI) and what to fix next.
agent: agora-facilitator
subtask: true
---
Show the health of the coach in $ARGUMENTS (or the active session). Resolve the shared data dir and confirm PERSONAS/<slug>/research/ exists. Run `python3 <repo>/scripts/coach_health.py "PERSONAS/<slug>"`: a deterministic 0-100 score, no AI judging it, which also writes PERSONAS/<slug>/coach-health.json for the coaches and /agora coach-update to read. Report in plain words: overall score and band (75+ strong, 50-74 ok, under 50 thin), the strongest and weakest topics, and the top 3-5 "Fix next" items. Say plainly that it measures grounding and findability, not whether the coach thinks like the person on a new question (that is /agora coach-eval), and that the numbers and concepts parts are heuristics. To fix what it finds, tell the user to run /agora coach-update, then run this again. NEVER write anything into inbox/.

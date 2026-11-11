---
name: coach-health
description: Show a coach's health score, a deterministic 0-100 score (no AI) for how well grounded the coach is in the person's real material and whether it can find it. Lists which topics are strong or thin and exactly what to fix next.
argument-hint: "[coach name] (optional — defaults to the active coach)"
disable-model-invocation: false
---

# /coach-health — is this coach grounded, and where is it thin?

The score is computed by `scripts/coach_health.py`. No AI judges it: the same files always
give the same number. That is what lets a coach trust it, and what lets you trust the coach.

## Step 0 — Resolve DATA_DIR and the coach

1. `$AGORA_DATA_DIR/personas` if set, otherwise `$HOME/.agora/personas`.
2. Slugify the name from `$ARGUMENTS` (or the active `/coach` session). Confirm
   `DATA_DIR/<slug>/research/` exists; if not, suggest `/coach <name>` to build them.

## Step 1 — Run it

```bash
python3 "$PLUGIN_ROOT/scripts/coach_health.py" "DATA_DIR/<slug>"
```

(Locate the script like /coach Step 3 locates `fetch_youtube.py`; `../../scripts/` from this
file works too.) It prints the report and writes `DATA_DIR/<slug>/coach-health.json`, which
`/coach`, `/roundtable` and `/coach-update` read.

## Step 2 — Report in plain words

Give: the overall score and band, the strongest and weakest topics, and the top 3-5 items
from "Fix next". Do not paste the whole table unless asked.

What each part means:
- **quotes**: share of quotes that are verified in their source
- **structure**: frontmatter, template sections, sensible size
- **numbers**: dollar amounts and percents that appear in a source (heuristic)
- **routing**: whether the persona index leads the coach to the right file for that file's own questions
- **rules**: sourced Decision Rules (aim for 5+)
- **sources / concepts / open work** (whole coach): transcripts actually used, his most repeated terms that are covered, and unextracted inbox files plus open gaps

## Limits to say out loud

- It measures grounding and findability. It does not measure whether the coach thinks like
  the person on a new question; `/coach-eval` does that. If health goes up and the eval
  doesn't, the health score is missing something.
- `numbers` and `concepts` are heuristics (spoken numbers like "five hundred" and generic
  phrases add noise). The uncovered terms are listed so you can ignore the noise.

To fix what it finds, run `/coach-update <name>`, then run this again to see the score move.
NEVER write anything into `inbox/`.

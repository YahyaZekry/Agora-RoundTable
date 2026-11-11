---
name: coach-eval
description: Measure how faithful a coach is to the real person. Builds a question set from the person's real answers plus situations he never addressed, has fresh coach agents answer cold, has separate judge agents grade each answer against what the real person said, and reports a percentage (held-out vs open-book). Failing answers become gaps that /coach-update can close.
argument-hint: "<coach name> [--build | --run]  (default: build the question set if missing, then run)"
disable-model-invocation: false
---

# /coach-eval — how close is this coach to the real person?

A persona can sound right and still give different advice from the real person. This
command measures that. The score is **closeness to what the real person actually said in
the same situation**. It is not a measure of whether the advice is correct.

Helper script: `scripts/eval_fidelity.py` (locate it like /coach Step 3 locates
`fetch_youtube.py`: `$PLUGIN_ROOT/scripts/`, or `../../scripts/` from this file).

## Step 0 — Resolve DATA_DIR and the coach

1. `$AGORA_DATA_DIR/personas` if set, otherwise `$HOME/.agora/personas`.
2. Slugify the name from `$ARGUMENTS` (or the active `/coach` session). Confirm
   `DATA_DIR/<slug>/persona.md` exists; if not, suggest `/coach <name>`.

## Step 1 — Build the question set (skip if `evals/questions.json` exists, unless `--build`)

Run `python3 eval_fidelity.py init DATA_DIR/<slug>` to create the template, then fill it:

1. Read `transcripts/` and `inbox/` and pick **10-20 moments where the person gives a
   concrete answer to a concrete situation** (a live-coaching call, a Q&A, an interview
   answer). Spread them across the person's topic areas, not just their most famous one.
2. For each moment write:
   - `question`: the situation as a user would say it, in the user's words. Do NOT include
     the person's answer, their framework names, or hints toward them.
   - `reference_points`: 2-5 short claims capturing what the real person said (the advice,
     the diagnosis, the number, the refusal). Take them from the transcript, not from
     `research/` or `persona.md`.
   - `must_mention`: framework names or figures a faithful answer would contain.
   - `source`: the transcript file.
   - `holdout`: `true` only if that transcript was never mined into `research/` (check
     `inbox/_sync-status.md` and the `sources:` lists in the research files). Most will be
     `false` on a coach whose transcripts were all mined. Say so to the user: it means the
     score is open-book. For an honest number, move a few transcripts into
     `DATA_DIR/<slug>/holdout/` before building a new coach, or add interview material
     that wasn't mined.
3. Show the user the questions and reference points and let them edit or drop items before
   saving. They know the person's real positions better than a summary does.

### Two kinds of question

Copying his answer and reasoning like him are different skills, so the set has both:

- **`copy` (the default, step 2 above):** a situation he really answered. Tests that the coach
  knows his material.
- **`new`:** 3-5 situations he never addressed (a bakery wants a subscription; a dentist wants
  to hire a first salesperson), spread across his topic areas. There is no real answer to copy,
  so set `"type": "new"` and write:
  - `rules`: 3-5 of his documented principles that apply, each as
    `{"rule": "...", "source": "research/<topic>.md"}`. Take them from the sourced **Decision
    Rules** sections, never from your own idea of what he would say.
  - `must_not`: 1-3 things he would never advise, from things he has said he is against.
  New items need no `reference_points` or `holdout`: they are always held-out and always graded
  by a judge. Show them to the user too; this is where the user's own knowledge of the person
  matters most.

## Step 2 — Collect the coach's answers (cold, one fresh agent per question)

`python3 eval_fidelity.py prompts DATA_DIR/<slug>` prints the questions as JSON.

Spawn one Agent per question, all in parallel (`run_in_background: false`), each fresh so
no answer contaminates another:

```
You are an AI embodiment of [Name] built from their public content.

1. Read your persona file: [DATA_DIR]/[slug]/persona.md
2. If research/_system-map.md exists and the question is broad, read it first. Then read
   the 1-3 research files that best match the question (use the Deep-Dive Sources index).
   Do NOT read evals/, holdout/, transcripts/ or inbox/.

A user says: "[question]"

Respond IN CHARACTER as [Name], as you would to this person: first person, your voice
and frameworks. No preamble. Return ONLY the response.
```

Write the answers to `DATA_DIR/<slug>/evals/answers.json` as `{"q1": "<answer>", ...}`.
Never show the coach agents `reference_points`.

## Step 3 — Judge

`python3 eval_fidelity.py judge DATA_DIR/<slug> --answers DATA_DIR/<slug>/evals/answers.json`
writes `evals/judge-prompts.json`. Spawn one **separate** Agent per prompt (parallel, not the
coach, out of character) with that prompt verbatim. Collect each agent's JSON reply into
`evals/grades.json` as a list.

## Step 4 — Score and report

```bash
python3 eval_fidelity.py score DATA_DIR/<slug> --answers DATA_DIR/<slug>/evals/answers.json \
  --grades DATA_DIR/<slug>/evals/grades.json --threshold 60
```

Report in a few lines: overall %, **copy held-out %** (does he know his material: the honest
number), copy open-book %, **new-situation %** (can he reason like him), and the weakest
answers with what they missed. Say plainly that the new-situation score means "consistent with
his documented rules", not "proven what he would say", and that it rests on the judge's
reading of those rules. Say plainly if everything was
open-book. A held-out score is only as good as the question set, so tell the user how many
questions it rests on.

## Step 5 — Turn misses into gaps

For each answer under 50%, find why and append to `research/_gaps.md` (same shape rules as
/coach-gaps; `Status: open`):

- The point is in a transcript but not in `research/` → **unmined** (free to fix).
- The point is in `research/` but the coach didn't use it → a **routing** problem: fix the
  `answers:`/`read_with:` lines in the research file's frontmatter, the persona's Deep-Dive
  Sources index, or `_system-map.md`. Re-run the eval to confirm.
- The point isn't in any file → **unresearched** or **user-only**.

Then tell the user to run `/coach-update <name>` to close them, and re-run `/coach-eval`
afterwards to see the score move. Keep each run's `report.json`; the trend is what shows
the plugin is improving.

Also run `scripts/coach_health.py` before and after the fixes. The health score is
deterministic and the eval is AI-graded, so each checks the other: if health goes up and the
eval score does not, tell the user the health score is missing something.

NEVER write into `inbox/`. It belongs to the user.

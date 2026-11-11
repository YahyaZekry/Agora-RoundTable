#!/usr/bin/env python3
"""Measure how close a coach's answers are to what the real person actually said.

The script never calls a model itself. The /coach-eval skill spawns fresh coach agents and
judge agents; this script prepares their prompts and does the scoring math.

Eval set: <persona-dir>/evals/questions.json
{
  "coach": "alex-hormozi",
  "items": [
    {
      "id": "q1",
      "question": "My moving company competes on hourly price. What do I do?",
      "source": "transcripts/give-me-42-minutes.md",
      "holdout": true,
      "reference_points": ["Build a premium VIP tier and open the sale with it",
                           "Stop competing on price; make the offers non-comparable"],
      "must_mention": ["VIP"]
    }
  ]
}
- reference_points: what the REAL person said in answer to that situation, as short claims.
- must_mention: names/terms a faithful answer should contain (framework names, numbers).
- holdout: true only if the source transcript was NOT mined into research/. Open-book items
  (holdout false) are reported separately because they flatter the coach.

Two kinds of item ("type"):
  copy (default)  A situation the person really answered. Graded on reference_points: did the
                  coach say what he said? Tests that the coach knows his material.
  new             A situation he NEVER addressed (a bakery wants a subscription). There is no
                  real answer to copy, so it is graded on his documented principles:
                    "rules":    [{"rule": "He prices at 5-10x cost", "source": "research/pricing.md"}]
                    "must_not": ["Recommends permanent discounting"]
                  Tests that the coach can reason like him. New items are always held-out, are
                  reported separately, and the score means "consistent with his documented
                  rules", not "proven what he would say". They always need judge grades.

Commands:
  init     <persona-dir>                         create an empty questions.json template
  prompts  <persona-dir>                         print the questions (for the coach agents)
  judge    <persona-dir> --answers answers.json  write judge-prompts.json (for judge agents)
  score    <persona-dir> --answers answers.json [--grades grades.json] [--threshold 60]

answers.json : {"q1": "<the coach's answer>", ...}
grades.json  : [{"id": "q1", "scores": [1, 0.5], "notes": "..."}, ...]   (1 / 0.5 / 0 per reference point)
Without grades.json, score falls back to a rough word-overlap estimate and says so.

Exit codes: 0 = overall score >= threshold, 1 = below threshold, 2 = bad arguments.
"""

import argparse
import json
import re
import sys
from pathlib import Path

STOPWORDS = set("""a an the and or but if then than that this these those to of in on for with at by from as is are was
were be been being it its you your i me my we our they their he she him her do does did not no so
just about into over out up down can could should would will what when where which who how why
more most very also have has had get got make made""".split())

TEMPLATE = {
    "coach": "<slug>",
    "items": [{
        "id": "q1",
        "question": "<a real situation, written the way a user would say it>",
        "source": "transcripts/<file>.md",
        "holdout": True,
        "reference_points": ["<what the real person said, as a short claim>"],
        "must_mention": ["<framework name or number a faithful answer contains>"],
    }, {
        "id": "n1",
        "type": "new",
        "question": "<a situation the person never addressed, in a user's words>",
        "rules": [{"rule": "<a documented rule he follows>", "source": "research/<topic>.md"}],
        "must_not": ["<something he would never advise>"],
    }],
}


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def load_items(persona_dir):
    path = persona_dir / "evals" / "questions.json"
    data = load_json(path)
    items = data.get("items", [])
    for it in items:
        need = "rules" if it.get("type") == "new" else "reference_points"
        if not it.get("id") or not it.get("question") or not it.get(need):
            print(f"ERROR: item {it.get('id', '?')} needs id, question and {need}", file=sys.stderr)
            sys.exit(2)
    return items


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if len(w) > 3 and w not in STOPWORDS}


def lexical_point_score(point, answer):
    pw = content_words(point)
    if not pw:
        return 0.0
    frac = len(pw & content_words(answer)) / len(pw)
    return 1.0 if frac >= 0.6 else 0.5 if frac >= 0.35 else 0.0


JUDGE_TEMPLATE = """You are grading an AI coach's answer against what the REAL person said about the same situation.
Step out of any persona. Be strict: a point counts only if the answer clearly makes it.

SITUATION:
{question}

ANSWER BEING GRADED:
{answer}

REFERENCE POINTS (what the real person said):
{points}

For each reference point give 1 (clearly made, same substance), 0.5 (partly or only implied),
or 0 (absent, or contradicted). Judge substance, not wording. Do not reward length.
Reply with JSON only: {{"id": "{id}", "scores": [<one number per point, in order>], "notes": "<one sentence>"}}"""

JUDGE_TEMPLATE_NEW = """You are grading an AI coach's answer to a situation the real person NEVER addressed.
There is no real answer to copy, so judge whether the answer is CONSISTENT WITH HIS DOCUMENTED RULES.
Step out of any persona. Be strict. Do not reward length.

SITUATION:
{question}

ANSWER BEING GRADED:
{answer}

STATEMENTS (a rule he follows, or a thing he would never do):
{points}

For a rule: 1 = the answer clearly applies it, 0.5 = partly or only implied, 0 = absent or contradicted.
For a statement starting with AVOIDS: 1 = the answer avoids it, 0.5 = borderline, 0 = the answer does it.
If the answer presents a quote, figure or story as his that is not in the rules, say so in notes.
Reply with JSON only: {{"id": "{id}", "scores": [<one number per statement, in order>], "notes": "<one sentence>"}}"""


def item_type(it):
    return "new" if it.get("type") == "new" else "copy"


def statements(it):
    """What the grader checks: reference points (copy) or rules + AVOIDS lines (new)."""
    if item_type(it) == "new":
        rules = [r["rule"] if isinstance(r, dict) else r for r in it.get("rules", [])]
        return rules + [f"AVOIDS: {m}" for m in it.get("must_not", [])]
    return it["reference_points"]


def cmd_init(persona_dir):
    out = persona_dir / "evals"
    out.mkdir(exist_ok=True)
    path = out / "questions.json"
    if path.exists():
        print(f"{path} already exists; not overwriting")
        return 0
    path.write_text(json.dumps(TEMPLATE, indent=2), encoding="utf-8")
    print(f"wrote template {path}")
    return 0


def cmd_prompts(persona_dir):
    items = load_items(persona_dir)
    print(json.dumps([{"id": i["id"], "question": i["question"]} for i in items], indent=2))
    return 0


def cmd_judge(persona_dir, answers_path):
    items, answers = load_items(persona_dir), load_json(answers_path)
    prompts = []
    for it in items:
        if it["id"] not in answers:
            continue
        points = "\n".join(f"{n}. {p}" for n, p in enumerate(statements(it), 1))
        template = JUDGE_TEMPLATE_NEW if item_type(it) == "new" else JUDGE_TEMPLATE
        prompts.append({"id": it["id"], "prompt": template.format(
            question=it["question"], answer=answers[it["id"]], points=points, id=it["id"])})
    out = persona_dir / "evals" / "judge-prompts.json"
    out.write_text(json.dumps(prompts, indent=2), encoding="utf-8")
    print(f"wrote {len(prompts)} judge prompt(s) to {out}")
    return 0


def mean(values):
    return sum(values) / len(values) if values else 0.0


def cmd_score(persona_dir, answers_path, grades_path, threshold):
    items, answers = load_items(persona_dir), load_json(answers_path)
    grades = {g["id"]: g for g in load_json(grades_path)} if grades_path else {}
    method = "judge-graded" if grades else "ROUGH word-overlap estimate, copy items only (no judge grades supplied)"
    rows, skipped = [], []
    for it in items:
        answer = answers.get(it["id"])
        if answer is None:
            continue
        kind, stmts = item_type(it), statements(it)
        graded = it["id"] in grades and len(grades[it["id"]].get("scores", [])) == len(stmts)
        if graded:
            pts = [float(s) for s in grades[it["id"]]["scores"]]
        elif kind == "copy":
            pts = [lexical_point_score(p, answer) for p in stmts]
        else:
            skipped.append(it["id"])
            continue
        must = it.get("must_mention", [])
        hits = [m for m in must if m.lower() in answer.lower()]
        rows.append({"id": it["id"], "type": kind, "score": mean(pts) * 100,
                     "holdout": True if kind == "new" else bool(it.get("holdout")),
                     "missed_points": [p for p, s in zip(stmts, pts) if s < 0.5],
                     "must_hit": f"{len(hits)}/{len(must)}" if must else "-",
                     "must_missed": [m for m in must if m not in hits]})
    if not rows:
        print("ERROR: no answered items to score", file=sys.stderr)
        return 2
    overall = mean([r["score"] for r in rows])
    copy_held = [r["score"] for r in rows if r["type"] == "copy" and r["holdout"]]
    copy_open = [r["score"] for r in rows if r["type"] == "copy" and not r["holdout"]]
    new = [r["score"] for r in rows if r["type"] == "new"]

    print(f"Scoring method: {method}\n")
    print(f"{'id':<8}{'score':>7}  {'kind':<6}{'set':<11}{'must-mention':<13}")
    for r in rows:
        print(f"{r['id']:<8}{r['score']:>6.0f}%  {r['type']:<6}{'held-out' if r['holdout'] else 'open-book':<11}{r['must_hit']:<13}")
    print(f"\nOverall:          {overall:.0f}%  ({len(rows)} questions)")
    if copy_held:
        print(f"Copy, held-out:   {mean(copy_held):.0f}%  ({len(copy_held)})   <- does he know his material? the honest number")
    if copy_open:
        print(f"Copy, open-book:  {mean(copy_open):.0f}%  ({len(copy_open)})   <- flattered: coach had this material")
    if new:
        print(f"New situations:   {mean(new):.0f}%  ({len(new)})   <- can he reason like him? consistent with his documented rules, not proof")
    if skipped:
        print(f"Skipped {len(skipped)} new-situation item(s) ({', '.join(skipped)}): they need judge grades.")
    print(f"Threshold: {threshold:.0f}%  ->  {'PASS' if overall >= threshold else 'BELOW'}")
    weak = [r for r in rows if r["score"] < 50]
    if weak:
        print("\nWeakest answers (missed points drive gap-closing):")
        for r in sorted(weak, key=lambda r: r["score"]):
            print(f"  {r['id']} ({r['score']:.0f}%): missed {r['missed_points']} {('and terms ' + str(r['must_missed'])) if r['must_missed'] else ''}")
    report = persona_dir / "evals" / "report.json"
    report.write_text(json.dumps({"method": method, "overall": overall,
                                  "copy_heldout": mean(copy_held) if copy_held else None,
                                  "copy_openbook": mean(copy_open) if copy_open else None,
                                  "new_situation": mean(new) if new else None,
                                  "skipped": skipped, "rows": rows}, indent=2), encoding="utf-8")
    print(f"\nreport: {report}")
    return 0 if overall >= threshold else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["init", "prompts", "judge", "score"])
    ap.add_argument("persona_dir")
    ap.add_argument("--answers")
    ap.add_argument("--grades")
    ap.add_argument("--threshold", type=float, default=60.0)
    args = ap.parse_args()
    persona_dir = Path(args.persona_dir).expanduser()
    if not persona_dir.is_dir():
        print(f"ERROR: {persona_dir} is not a directory", file=sys.stderr)
        return 2
    if args.command == "init":
        return cmd_init(persona_dir)
    if args.command == "prompts":
        return cmd_prompts(persona_dir)
    if not args.answers:
        print("ERROR: --answers is required", file=sys.stderr)
        return 2
    if args.command == "judge":
        return cmd_judge(persona_dir, args.answers)
    return cmd_score(persona_dir, args.answers, args.grades, args.threshold)


if __name__ == "__main__":
    sys.exit(main())

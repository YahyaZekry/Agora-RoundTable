#!/usr/bin/env python3
"""Which research files must a coach read before answering this question? (no AI)

Run it before every reply. It ranks the coach's research files against the question with the
same TF-IDF routing the health score uses, but it can also see each file's frontmatter
(title, covers, answers), so it routes better than the persona index alone.

Output:
  BROAD      3+ files match about equally, or the best match is weak: read research/_system-map.md
             first, then the listed files
  NARROW     one or two files clearly match: read just those
  NO MATCH   nothing in the research matches: the question is probably outside the person's
             documented material. Say so in character; do not fill the gap from general knowledge.

It also prints each file's health band from coach-health.json (if present). For a `thin`
topic the coach should say it has not gone deep on it.

Usage:
  python3 route_question.py <persona-dir> "the user's question"
  python3 route_question.py <persona-dir> "the user's question" --json
  python3 route_question.py <persona-dir> "..." --max-files 3

Exit codes: 0 always when it ran, 2 on bad arguments.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coach_health as ch  # noqa: E402

MIN_SCORE = 0.05        # below this a file does not count as a match
CLOSE_RATIO = 0.6       # a file "matches about equally" if it scores >= 60% of the top file
BROAD_AT = 3            # this many equal matches means a broad question
WEAK_TOP = 0.3          # a weak best match with 2+ close files also counts as broad
VERY_WEAK_TOP = 0.2     # a very weak best match is treated as a broad question


def load_bands(persona_dir):
    path = persona_dir / "coach-health.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {stem: t.get("band", "unknown") for stem, t in data.get("topics", {}).items()}


def route(persona_dir, question, max_files=3):
    research = persona_dir / "research"
    files = ch.topic_files(research) if research.is_dir() else []
    if not files:
        return {"route": "no_research", "files": [], "question": question}
    stems = [f.stem for f in files]
    index = ch.index_blocks(persona_dir, stems)
    meta_by_stem, docs = {}, {}
    for f in files:
        meta, _ = ch.vr.parse_frontmatter(ch.read_raw(f))
        meta = meta or {}
        meta_by_stem[f.stem] = meta
        extra = [str(meta.get("title", "")), str(meta.get("covers", ""))]
        answers = meta.get("answers")
        if isinstance(answers, list):
            extra += answers
        docs[f.stem] = index.get(f.stem, "") + " " + " ".join(extra)

    ranked = ch.tfidf_rank(question, docs)
    top = ranked[0][0]
    if top < MIN_SCORE:
        return {"route": "no_match", "files": [], "question": question}

    close = [(s, n) for s, n in ranked if s >= max(MIN_SCORE, CLOSE_RATIO * top)]
    weak = top < WEAK_TOP
    kind = "broad" if (len(close) >= BROAD_AT or (weak and len(close) >= 2) or top < VERY_WEAK_TOP) else "narrow"
    chosen = close[:max_files] if kind == "broad" else [(s, n) for s, n in ranked if s >= max(MIN_SCORE, 0.5 * top)][:2]

    bands = load_bands(persona_dir)
    out = []
    for score, stem in chosen:
        rw = meta_by_stem[stem].get("read_with", [])
        out.append({"file": str((research / f"{stem}.md")), "topic": stem, "match": round(score, 2),
                    "band": bands.get(stem, "unknown"),
                    "read_with": rw if isinstance(rw, list) else []})
    result = {"route": kind, "files": out, "question": question}
    smap = research / "_system-map.md"
    if kind == "broad" and smap.is_file():
        result["read_first"] = str(smap)
    return result


def render(r):
    lines = [f"Question: {r['question']}", ""]
    if r["route"] == "no_research":
        lines.append("ROUTE: NO RESEARCH FOLDER. Answer from persona.md only and say you have not gone deep on this.")
        return "\n".join(lines)
    if r["route"] == "no_match":
        lines += ["ROUTE: NO MATCH",
                  "Nothing in this coach's research matches the question. Check persona.md > Topics They Defer On.",
                  "If it is outside his documented material, say so in character and, at most, reason from his",
                  "principles while marking it as extension. Do not fill the gap from general knowledge."]
        return "\n".join(lines)
    lines.append(f"ROUTE: {r['route'].upper()}")
    if r.get("read_first"):
        lines.append(f"READ FIRST: {r['read_first']}")
    lines.append("READ:")
    for i, f in enumerate(r["files"], 1):
        rw = f" (read with: {', '.join(f['read_with'])})" if f["read_with"] else ""
        lines.append(f"  {i}. {f['file']}   match {f['match']}, band {f['band']}{rw}")
    thin = [f["topic"] for f in r["files"] if f["band"] == "thin"]
    if thin:
        lines.append(f"THIN: {', '.join(thin)}. Say in character that you have not gone deep on this, and stay within the file.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("persona_dir")
    ap.add_argument("question", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-files", type=int, default=3)
    args = ap.parse_args()
    persona_dir = Path(args.persona_dir).expanduser()
    if not persona_dir.is_dir():
        print(f"ERROR: {persona_dir} is not a directory", file=sys.stderr)
        return 2
    result = route(persona_dir, " ".join(args.question), args.max_files)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

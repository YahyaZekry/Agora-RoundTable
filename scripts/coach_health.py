#!/usr/bin/env python3
"""Coach health score: a deterministic 0-100 score for how well-grounded a coach is.

No AI is involved. The same files always give the same score. The AI reads the result
(coach-health.json) to know which topics are solid and which are thin; the score does not
need the AI to be trusted.

What it measures: whether the coach is GROUNDED in the person's real material and can FIND
it. It does not measure whether the coach thinks like the person on a new question; that
is what /coach-eval is for, and the eval is how this score gets checked.

Per topic file (research/*.md except _gaps.md and _system-map.md):
  quotes     tagged quotes verified in their source (untagged long quotes count against)
  structure  frontmatter keys, template sections, sane size
  numbers    dollar amounts / percents / multiples whose digits appear in a source (heuristic)
  routing    each question in the file's `answers:` finds the file via the persona.md index
             lines and the system map (TF-IDF, top-k). A file the index can't route to scores 0.
  rules      sourced Decision Rules (target: 5+)

Per coach:
  sources    transcripts that research/ actually references
  concepts   his most-repeated terms across transcripts that appear in research/ (heuristic;
             the uncovered terms are listed so a person can ignore the noise)
  open_work  inbox files not yet logged, plus open gaps

Bands: 75+ strong, 50-74 ok, under 50 thin.

Primary-material caps (so a coach built only from web summaries can never look "strong"):
  - a topic whose declared sources are all web:/book: references is capped at 74
  - a coach with no transcripts and no inbox material is capped at 49 overall

Usage:
  python3 coach_health.py <persona-dir>             # print report, write coach-health.json
  python3 coach_health.py <persona-dir> --json      # JSON to stdout, nothing written
  python3 coach_health.py <persona-dir> --no-write
  python3 coach_health.py <persona-dir> --fail-under 60

Exit codes: 0 ok, 1 overall score below --fail-under, 2 bad arguments.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_quotes as cq  # noqa: E402
import validate_research as vr  # noqa: E402

SPECIAL = {"_gaps.md", "_system-map.md"}
WEIGHTS = {"quotes": 25, "structure": 15, "numbers": 10, "routing": 20, "rules": 15}
RULES_TARGET = 5
STRONG, OK = 75, 50
TOPIC_CAP_NO_LOCAL_SOURCE = 74
COACH_CAP_NO_PRIMARY = 49

STOP = set("""the and you that this with for are was have but not they what when your can from just like know going
really about there their would could should will its get got one all out here then than them these those into over
some more very because been being were which who how why where also way thing things lot kind sort say said see
make made want need think right okay yeah actually basically literally people time guys gonna dont doesnt cant wont
thats youre theyre ive youve weve our ours has had does did too any each every other another only even still much
many let lets per new good great best first back take come look doing done put use used say says whatever something
anything everything someone anyone nothing never always sometimes maybe probably""".split())


# --------------------------------------------------------------------------- helpers
def tokens(text):
    out = []
    for w in re.findall(r"[^\W\d_]{3,}", cq.norm(text)):
        if w in STOP:
            continue
        if len(w) > 4 and w.endswith("s"):
            w = w[:-1]
        if len(w) > 4 and w.startswith("\u0627\u0644"):  # Arabic "al-" prefix
            w = w[2:]
        out.append(w)
    return out


def has_local_source(meta, persona_dir):
    """True/False if the file declares sources (any local file?), None if it declares none."""
    declared = meta.get("sources")
    if not isinstance(declared, list) or not declared:
        return None
    return any(cq.resolve(persona_dir, ref)[0] == "file" for ref in declared)


def primary_files(persona_dir):
    found = []
    for sub in ("transcripts", "inbox"):
        d = persona_dir / sub
        if d.is_dir():
            found += [p for p in d.iterdir() if p.is_file() and not p.name.startswith(("_", "."))]
    return found


def band(score):
    return "strong" if score >= STRONG else "ok" if score >= OK else "thin"


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def read_raw(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def strip_frontmatter(text):
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)


def topic_files(research):
    return sorted(f for f in research.glob("*.md") if f.name not in SPECIAL)


# --------------------------------------------------------------------------- per-topic components
def score_quotes(path, persona_dir):
    findings, unsourced = cq.scan_file(path, persona_dir)
    total = len(findings) + len(unsourced)
    if total == 0:
        return None, []
    credit = {"OK": 1.0, "NEAR": 0.5, "UNCHECKABLE": 0.5}
    got = sum(credit.get(f["status"], 0.0) for f in findings)
    notes = []
    bad = sum(1 for f in findings if f["status"] in ("NOT_FOUND", "NO_SOURCE_FILE"))
    near = sum(1 for f in findings if f["status"] == "NEAR")
    if bad:
        notes.append(f"{bad} quote(s) not found in the cited source")
    if near:
        notes.append(f"{near} quote(s) only near-match their source")
    if unsourced:
        notes.append(f"{len(unsourced)} long quote(s) with no [src: ...] tag")
    return 100 * got / total, notes


def score_structure(text):
    meta, body = vr.parse_frontmatter(text)
    notes = []
    if meta is None:
        keys = 0.0
        notes.append("no frontmatter")
    else:
        present = [k for k in vr.REQUIRED_KEYS if meta.get(k)]
        keys = len(present) / len(vr.REQUIRED_KEYS)
        missing = [k for k in vr.REQUIRED_KEYS if k not in present]
        if missing:
            notes.append("frontmatter missing: " + ", ".join(missing))
    found = [s for s in vr.REQUIRED_SECTIONS
             if re.search(rf"^#{{1,4}}\s+.*{re.escape(s)}", body, flags=re.M | re.I)]
    sections = len(found) / len(vr.REQUIRED_SECTIONS)
    missing_sections = [s for s in vr.REQUIRED_SECTIONS if s not in found]
    if missing_sections:
        notes.append("missing sections: " + ", ".join(missing_sections))
    words = len(body.split())
    size = 1.0 if vr.MIN_WORDS <= words <= vr.MAX_WORDS else 0.0
    if not size:
        notes.append(f"{words} words (aim for {vr.MIN_WORDS}-{vr.MAX_WORDS})")
    return 100 * (0.4 * keys + 0.4 * sections + 0.2 * size), notes, (meta or {})


FIG_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?%|\d+(?:\.\d+)?\s?x\b|\d{2,}[\d,]*(?:\.\d+)?")
NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def core_number(fig):
    m = NUM_RE.search(fig)
    return m.group(0).replace(",", "").rstrip(".") if m else None


def source_numbers(persona_dir, meta):
    """Numbers found in the file's declared sources, else in all transcripts + inbox text."""
    paths = []
    declared = meta.get("sources")
    if isinstance(declared, list):
        for ref in declared:
            kind, p = cq.resolve(persona_dir, ref)
            if kind == "file" and p.suffix.lower() in cq.TEXT_SUFFIXES:
                paths.append(p)
    if not paths:
        for sub in ("transcripts", "inbox"):
            d = persona_dir / sub
            if d.is_dir():
                paths += [p for p in sorted(d.iterdir()) if p.suffix.lower() in cq.TEXT_SUFFIXES and not p.name.startswith("_")]
    nums = set()
    for p in paths:
        for m in NUM_RE.findall(cq.ascii_digits(read_raw(p))):
            nums.add(m.replace(",", "").rstrip("."))
    return nums, bool(paths)


def score_numbers(body, meta, persona_dir):
    if str(meta.get("source_type", "")).lower() == "secondary":
        return None, []
    nums, have_sources = source_numbers(persona_dir, meta)
    if not have_sources:
        return None, []
    body = cq.ascii_digits(re.sub(r"```.*?```", "", body, flags=re.S))
    figs = {}
    for m in FIG_RE.finditer(body):
        fig = m.group(0).strip()
        core = core_number(fig)
        if core is None:
            continue
        plain_small = "." not in core and int(core) < 10
        if plain_small and not re.search(r"[$%x]", fig):
            continue
        if re.fullmatch(r"(19|20)\d\d", core):
            continue
        figs[fig] = core
    if not figs:
        return None, []
    missing = [f for f, c in figs.items() if c not in nums]
    score = 100 * (len(figs) - len(missing)) / len(figs)
    notes = [f"{len(missing)} of {len(figs)} figures not found in sources, e.g. " + ", ".join(sorted(missing)[:4])] if missing else []
    return score, notes


def score_rules(body):
    m = re.search(r"^#{1,4}\s+Decision Rules\s*\n(.*?)(?=^#{1,4}\s|\Z)", body, flags=re.M | re.S | re.I)
    if not m:
        return 0.0, ["no Decision Rules section"]
    bullets = [ln for ln in m.group(1).splitlines() if ln.lstrip().startswith(("-", "*"))]
    sourced = [ln for ln in bullets if "[src:" in ln]
    score = 100 * min(1.0, len(sourced) / RULES_TARGET)
    notes = [] if len(sourced) >= RULES_TARGET else [f"{len(sourced)} sourced decision rule(s), aim for {RULES_TARGET}+"]
    return score, notes


# --------------------------------------------------------------------------- routing
def index_blocks(persona_dir, stems):
    """Text a coach can see about each file BEFORE opening it: persona.md index + system map."""
    blocks = {s: [] for s in stems}
    for fname in ("persona.md", "research/_system-map.md"):
        path = persona_dir / fname
        if not path.is_file():
            continue
        lines = read_raw(path).splitlines()
        for i, line in enumerate(lines):
            for s in stems:
                if f"research/{s}.md" in line:
                    chunk = [line]
                    j = i + 1
                    while j < len(lines) and lines[j].startswith((" ", "\t")) and lines[j].strip():
                        chunk.append(lines[j])
                        j += 1
                    blocks[s].append(" ".join(chunk))
    return {s: " ".join(v) for s, v in blocks.items()}


def tfidf_rank(question, docs):
    names = sorted(docs)
    doc_tokens = {n: Counter(tokens(docs[n])) for n in names}
    n_docs = len(names)
    df = Counter()
    for c in doc_tokens.values():
        df.update(c.keys())
    idf = {t: math.log((n_docs + 1) / (df[t] + 1)) + 1 for t in df}

    def vec(counter):
        return {t: (1 + math.log(c)) * idf.get(t, 1.0) for t, c in counter.items()}

    qv = vec(Counter(tokens(question)))
    qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
    scored = []
    for n in names:
        dv = vec(doc_tokens[n])
        dn = math.sqrt(sum(v * v for v in dv.values())) or 1.0
        dot = sum(qv[t] * dv[t] for t in qv if t in dv)
        scored.append((dot / (qn * dn), n))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored


def score_routing(stem, questions, docs, k):
    if not questions:
        return None, []
    hits, missed = 0, []
    for q in questions:
        ranked = tfidf_rank(q, docs)[:k]
        if any(n == stem and s > 0 for s, n in ranked):
            hits += 1
        else:
            missed.append(q)
    notes = []
    if missed:
        shown = "; ".join(f'"{q}"' for q in missed[:2])
        notes.append(f"index doesn't route {len(missed)}/{len(questions)} of its own questions here, e.g. {shown}")
    return 100 * hits / len(questions), notes


# --------------------------------------------------------------------------- per-coach components
def score_sources(persona_dir, research_text):
    tdir = persona_dir / "transcripts"
    files = sorted(p for p in tdir.glob("*.md")) if tdir.is_dir() else []
    if not files:
        return None, []
    low = research_text.lower()
    unused = [p.name for p in files if p.name.lower() not in low and p.stem.lower() not in low]
    score = 100 * (len(files) - len(unused)) / len(files)
    notes = [f"{len(unused)} of {len(files)} transcripts never referenced in research/, e.g. " + ", ".join(unused[:4])] if unused else []
    return score, notes


def score_concepts(persona_dir, research_norm):
    tdir = persona_dir / "transcripts"
    files = sorted(tdir.glob("*.md")) if tdir.is_dir() else []
    if len(files) < 2:
        return None, [], []
    df, total = Counter(), Counter()
    for p in files:
        words = cq.norm(strip_frontmatter(read_raw(p))).split()
        seen = set()
        for n in (2, 3):
            for i in range(len(words) - n + 1):
                gram = words[i:i + n]
                if any(w in STOP or w.isdigit() or len(w) < 3 for w in (gram[0], gram[-1])):
                    continue
                if any(w.isdigit() for w in gram):
                    continue
                phrase = " ".join(gram)
                total[phrase] += 1
                seen.add(phrase)
        df.update(seen)
    min_df = 2 if len(files) < 6 else max(3, math.ceil(0.25 * len(files)))
    cands = [p for p in df if df[p] >= min_df]
    cands.sort(key=lambda p: (-df[p], -total[p], -len(p.split()), p))
    chosen = []
    for p in sorted(cands[:200], key=lambda p: (-len(p.split()), -df[p], p)):
        if any(p in c and df[c] >= 0.8 * df[p] for c in chosen):
            continue
        chosen.append(p)
    chosen.sort(key=lambda p: (-df[p], -total[p], p))
    chosen = chosen[:30]
    if not chosen:
        return None, [], []
    uncovered = [p for p in chosen if p not in research_norm]
    score = 100 * (len(chosen) - len(uncovered)) / len(chosen)
    return score, [], uncovered


def parse_gap_count(gaps_text):
    n = len(re.findall(r"^\s*-\s\[ \]", gaps_text, flags=re.M))
    n += len(re.findall(r"status:\s*open", gaps_text, flags=re.I))
    n += len(re.findall(r"^\|.*\|\s*open\s*\|?\s*$", gaps_text, flags=re.M | re.I))
    return n


def score_open_work(persona_dir):
    inbox = persona_dir / "inbox"
    unlogged = []
    if inbox.is_dir():
        status = read_raw(inbox / "_sync-status.md").lower()
        for p in sorted(inbox.iterdir()):
            if p.is_file() and not p.name.startswith(("_", ".")) and p.name.lower() not in status:
                unlogged.append(p.name)
    gaps = persona_dir / "research" / "_gaps.md"
    open_gaps = parse_gap_count(read_raw(gaps)) if gaps.is_file() else 0
    score = max(0.0, 100 - 10 * len(unlogged) - 3 * open_gaps)
    notes = []
    if unlogged:
        notes.append(f"{len(unlogged)} inbox file(s) not yet extracted: " + ", ".join(unlogged[:4]))
    if open_gaps:
        notes.append(f"{open_gaps} open gap(s) in research/_gaps.md")
    return score, notes


# --------------------------------------------------------------------------- main
def weighted(components):
    num = den = 0.0
    for name, val in components.items():
        if val is not None:
            num += WEIGHTS[name] * val
            den += WEIGHTS[name]
    return num / den if den else 0.0


def analyze(persona_dir):
    research = persona_dir / "research"
    files = topic_files(research) if research.is_dir() else []
    stems = [f.stem for f in files]
    docs = index_blocks(persona_dir, stems)
    k = 1 if len(stems) <= 3 else 3

    topics = {}
    for f in files:
        text = read_raw(f)
        q_score, q_notes = score_quotes(f, persona_dir)
        s_score, s_notes, meta = score_structure(text)
        _, body = vr.parse_frontmatter(text)
        n_score, n_notes = score_numbers(body, meta, persona_dir)
        questions = meta.get("answers", []) if isinstance(meta.get("answers"), list) else []
        r_score, r_notes = score_routing(f.stem, questions, docs, k) if len(stems) > 1 else (None, [])
        d_score, d_notes = score_rules(body)
        comps = {"quotes": q_score, "structure": s_score, "numbers": n_score, "routing": r_score, "rules": d_score}
        score = weighted(comps)
        cap_notes = []
        if has_local_source(meta, persona_dir) is False and score > TOPIC_CAP_NO_LOCAL_SOURCE:
            score = TOPIC_CAP_NO_LOCAL_SOURCE
            cap_notes.append("capped at 74: no local primary source (only web:/book: references); add transcripts or inbox material")
        topics[f.stem] = {
            "score": round(score, 1), "band": band(score),
            "components": {c: (None if v is None else round(v, 1)) for c, v in comps.items()},
            "notes": cap_notes + q_notes + s_notes + n_notes + r_notes + d_notes,
        }

    research_text = "\n".join(read_raw(p) for p in sorted(research.glob("*.md")) if p.name != "_gaps.md") if research.is_dir() else ""
    src_score, src_notes = score_sources(persona_dir, research_text)
    con_score, _, uncovered = score_concepts(persona_dir, cq.norm(research_text))
    open_score, open_notes = score_open_work(persona_dir)
    persona_level = {"sources": src_score, "concepts": con_score, "open_work": open_score}
    topic_mean = mean([t["score"] for t in topics.values()])
    persona_mean = mean(persona_level.values())
    overall = topic_mean if persona_mean is None else (0.7 * topic_mean + 0.3 * persona_mean) if topic_mean is not None else persona_mean
    overall = overall if overall is not None else 0.0
    no_primary = not primary_files(persona_dir)
    coach_notes = []
    if no_primary:
        coach_notes.append("no transcripts or inbox material: built from secondary summaries only; capped at 49 overall. Add transcripts or books to inbox/ and run /coach-update")
        overall = min(overall, COACH_CAP_NO_PRIMARY)

    actions = []
    for stem, t in sorted(topics.items(), key=lambda kv: (kv[1]["score"], kv[0])):
        for note in t["notes"]:
            actions.append(f"research/{stem}.md: {note}")
    actions = [f"coach: {n}" for n in coach_notes] + actions
    actions += [f"coach: {n}" for n in src_notes + open_notes]
    if uncovered:
        actions.append("coach: his repeated terms missing from research/: " + ", ".join(uncovered[:10]))
    return {
        "overall": round(overall, 1), "band": band(overall),
        "topics": topics,
        "coach": {"sources": None if src_score is None else round(src_score, 1),
                  "concepts": None if con_score is None else round(con_score, 1),
                  "open_work": round(open_score, 1),
                  "primary_material": not no_primary},
        "uncovered_terms": uncovered[:15],
        "next_actions": actions[:25],
        "method": "deterministic, no AI; same files give the same score",
    }


def render(report):
    out = [f"Coach health: {report['overall']:.0f}/100 ({report['band']})", "",
           f"{'topic':<38}{'score':>6}  {'band':<7}quotes struct numbers routing rules"]
    for stem, t in sorted(report["topics"].items(), key=lambda kv: (kv[1]["score"], kv[0])):
        c = t["components"]
        fmt = lambda v: "  n/a" if v is None else f"{v:>5.0f}"
        out.append(f"{stem[:37]:<38}{t['score']:>6.0f}  {t['band']:<7}{fmt(c['quotes'])}  {fmt(c['structure'])}   {fmt(c['numbers'])}   {fmt(c['routing'])} {fmt(c['rules'])}")
    c = report["coach"]
    fmt = lambda v: "n/a" if v is None else f"{v:.0f}"
    out += ["", f"Coach-wide: sources {fmt(c['sources'])} | concepts {fmt(c['concepts'])} | open work {fmt(c['open_work'])} | primary material {'yes' if c.get('primary_material') else 'NONE'}"]
    if report["next_actions"]:
        out += ["", "Fix next:"] + [f"  - {a}" for a in report["next_actions"][:12]]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("persona_dir")
    ap.add_argument("--json", action="store_true", help="print JSON, write nothing")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--fail-under", type=float)
    args = ap.parse_args()
    persona_dir = Path(args.persona_dir).expanduser()
    if not (persona_dir / "research").is_dir():
        print(f"ERROR: {persona_dir}/research does not exist", file=sys.stderr)
        return 2
    report = analyze(persona_dir)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
        if not args.no_write:
            out = persona_dir / "coach-health.json"
            out.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"\nwrote {out}")
    return 1 if args.fail_under is not None and report["overall"] < args.fail_under else 0


if __name__ == "__main__":
    sys.exit(main())

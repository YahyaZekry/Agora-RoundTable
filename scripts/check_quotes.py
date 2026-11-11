#!/usr/bin/env python3
"""Check that quotes in a coach's research/ files really appear in the sources they cite.

A quote is any double-quoted text of 15+ characters followed (within ~100 characters) by
a source tag:   "the quote" [src: transcripts/foo.md]

For each tagged quote the script looks in the cited file and reports one of:
  OK             the words appear in the source (punctuation/case ignored)
  NEAR           most of the quote's word-triples appear, but not all (a paraphrase,
                 or a transcription difference). Not a verbatim quote: fix or reword.
  NOT_FOUND      the source exists but the quote is not in it
  NO_SOURCE_FILE the cited file does not exist
  UNCHECKABLE    the source is web:/book: or a binary file that cannot be read here

Quotes with no [src: ...] tag are listed as UNSOURCED when they are 8+ words long.

Usage:
  python3 check_quotes.py <persona-dir>               # check every research/*.md
  python3 check_quotes.py <persona-dir> --file research/marketing-and-offers.md
  python3 check_quotes.py <persona-dir> --strict      # NEAR also fails
  python3 check_quotes.py <persona-dir> --json

Exit codes: 0 = clean, 1 = NOT_FOUND / NO_SOURCE_FILE found (or NEAR with --strict),
            2 = bad arguments.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".json", ".vtt", ".srt", ".html", ".csv"}
QUOTE_CHARS = '"\u201c\u201d\u00ab\u00bb'
OPEN = r'(?<!\w)["\u201c\u00ab](?=[\w$\[(])'   # a real opening quote, not a stray closing one
CLOSE = r'(?<=\S)["\u201d\u00bb]'
TAGGED_RE = re.compile(
    OPEN + r'(?P<q>[^"\u201c\u201d\u00ab\u00bb\n]{15,}?)' + CLOSE +
    r'(?P<gap>[^\[\n"\u201c\u201d\u00ab\u00bb]{0,100}?)'
    r'\[src:\s*(?P<src>[^\]]+?)\s*\]'
)
ANY_QUOTE_RE = re.compile(OPEN + r'(?P<q>[^"\u201c\u201d\u00ab\u00bb\n]{15,}?)' + CLOSE)
ELLIPSIS_RE = re.compile(r"\.{3}|\u2026|\[\.\.\.\]")
NEAR_THRESHOLD = 0.85
MIN_FRAGMENT_WORDS = 3
MIN_UNSOURCED_WORDS = 8

_cache = {}


_DIGIT_MAP = {**{0x0660 + i: ord("0") + i for i in range(10)},   # Arabic-Indic digits
              **{0x06F0 + i: ord("0") + i for i in range(10)},   # Extended Arabic-Indic digits
              0x066B: ord("."), 0x066C: ord(",")}
_LETTER_MAP = {ord(c): "\u0627" for c in "\u0623\u0625\u0622\u0671"}  # alef variants -> bare alef
_LETTER_MAP.update({0x0649: "\u064a", 0x0629: "\u0647", 0x0640: None})  # ى->ي, ة->ه, drop tatweel


def ascii_digits(text):
    """Arabic-Indic digits and separators -> ASCII, so figures compare across scripts."""
    return text.translate(_DIGIT_MAP)


def norm(text):
    """Case/punctuation/diacritic-insensitive form. Works for any script, Arabic included."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))  # accents, Arabic harakat
    text = ascii_digits(text).casefold().replace("\u2019", "'").replace("\u2018", "'")
    text = text.translate(_LETTER_MAP)
    text = re.sub(r"\[[^\]]*\]", " ", text)  # editorial insertions like [I learned]
    text = re.sub(r"[^\w']+", " ", text).replace("'", "").replace("_", " ")
    return re.sub(r"\s+", " ", text).strip()


def trigrams(words):
    return {tuple(words[i:i + 3]) for i in range(len(words) - 2)}


def read_source(path):
    """Return (normalized_text, None) or (None, reason)."""
    key = str(path)
    if key in _cache:
        return _cache[key]
    result = (None, "unreadable")
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        try:
            result = (norm(path.read_text(encoding="utf-8", errors="replace")), None)
        except OSError as exc:
            result = (None, str(exc))
    elif suffix == ".pdf":
        if shutil.which("pdftotext"):
            try:
                out = subprocess.run(["pdftotext", str(path), "-"], capture_output=True,
                                     text=True, timeout=120).stdout
                result = (norm(out), None)
            except (OSError, subprocess.SubprocessError) as exc:
                result = (None, str(exc))
        else:
            result = (None, "pdf (pdftotext not installed)")
    else:
        result = (None, "binary file")
    _cache[key] = result
    return result


def resolve(persona_dir, ref):
    ref = ref.split("#", 1)[0].strip()
    if ref.startswith(("web:", "book:", "http://", "https://")):
        return "uncheckable", None
    path = persona_dir / ref
    if path.is_file():
        return "file", path
    for prefix in ("transcripts", "inbox", "research"):
        alt = persona_dir / prefix / ref
        if alt.is_file():
            return "file", alt
    return "missing", None


def check_fragment(fragment, source_text):
    words = norm(fragment).split()
    if len(words) < MIN_FRAGMENT_WORDS:
        return "OK", 1.0
    needle = " ".join(words)
    if needle in source_text:
        return "OK", 1.0
    src_tri = trigrams(source_text.split())
    q_tri = trigrams(words)
    if not q_tri:
        return "NOT_FOUND", 0.0
    overlap = len(q_tri & src_tri) / len(q_tri)
    return ("NEAR" if overlap >= NEAR_THRESHOLD else "NOT_FOUND"), overlap


def check_quote(quote, sources, persona_dir):
    """Worst-case status across fragments; best-case across the cited sources."""
    best = None
    notes = []
    for ref in sources:
        kind, path = resolve(persona_dir, ref)
        if kind == "uncheckable":
            outcome = ("UNCHECKABLE", 0.0, ref)
        elif kind == "missing":
            outcome = ("NO_SOURCE_FILE", 0.0, ref)
        else:
            text, reason = read_source(path)
            if text is None:
                outcome = ("UNCHECKABLE", 0.0, f"{ref} ({reason})")
            else:
                worst, worst_score = "OK", 1.0
                for frag in ELLIPSIS_RE.split(quote):
                    status, score = check_fragment(frag, text)
                    rank = {"OK": 0, "NEAR": 1, "NOT_FOUND": 2}[status]
                    if rank > {"OK": 0, "NEAR": 1, "NOT_FOUND": 2}[worst]:
                        worst, worst_score = status, score
                outcome = (worst, worst_score, ref)
        notes.append(outcome[2])
        order = {"OK": 0, "NEAR": 1, "UNCHECKABLE": 2, "NOT_FOUND": 3, "NO_SOURCE_FILE": 4}
        if best is None or order[outcome[0]] < order[best[0]]:
            best = outcome
    return best[0], best[1], notes


def paragraphs(text):
    for block in re.split(r"\n\s*\n", text):
        yield " ".join(block.split())


def scan_file(path, persona_dir):
    findings, unsourced = [], []
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)  # skip frontmatter
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # skip code blocks (templates)
    for para in paragraphs(text):
        tagged_spans = []
        for m in TAGGED_RE.finditer(para):
            tagged_spans.append((m.start("q"), m.end("q")))
            sources = [s.strip() for s in m.group("src").split(";") if s.strip()]
            status, score, notes = check_quote(m.group("q"), sources, persona_dir)
            findings.append({"file": path.name, "status": status, "score": round(score, 2),
                             "quote": m.group("q"), "sources": notes})
        for m in ANY_QUOTE_RE.finditer(para):
            if any(s <= m.start("q") < e for s, e in tagged_spans):
                continue
            if len(m.group("q").split()) >= MIN_UNSOURCED_WORDS:
                unsourced.append({"file": path.name, "quote": m.group("q")})
    return findings, unsourced


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("persona_dir")
    ap.add_argument("--file", help="check one research file (path relative to persona dir)")
    ap.add_argument("--strict", action="store_true", help="NEAR also counts as failure")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    persona_dir = Path(args.persona_dir).expanduser()
    if not persona_dir.is_dir():
        print(f"ERROR: {persona_dir} is not a directory", file=sys.stderr)
        return 2
    research = persona_dir / "research"
    files = [persona_dir / args.file] if args.file else sorted(research.glob("*.md")) if research.is_dir() else []
    files = [f for f in files if f.name != "_gaps.md"]
    if not files:
        print("ERROR: no research files found", file=sys.stderr)
        return 2

    all_findings, all_unsourced = [], []
    for f in files:
        found, unsrc = scan_file(f, persona_dir)
        all_findings += found
        all_unsourced += unsrc

    counts = {}
    for item in all_findings:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    failing = {"NOT_FOUND", "NO_SOURCE_FILE"} | ({"NEAR"} if args.strict else set())
    failed = any(i["status"] in failing for i in all_findings)

    if args.json:
        print(json.dumps({"counts": counts, "findings": all_findings,
                          "unsourced": all_unsourced, "failed": failed}, indent=2))
        return 1 if failed else 0

    print(f"Checked {len(files)} research file(s), {len(all_findings)} tagged quote(s).")
    for status in ("OK", "NEAR", "NOT_FOUND", "NO_SOURCE_FILE", "UNCHECKABLE"):
        if counts.get(status):
            print(f"  {status:<15} {counts[status]}")
    print(f"  {'UNSOURCED':<15} {len(all_unsourced)}  (quotes of {MIN_UNSOURCED_WORDS}+ words with no [src: ...] tag)")
    for item in all_findings:
        if item["status"] in ("NEAR", "NOT_FOUND", "NO_SOURCE_FILE"):
            q = item["quote"] if len(item["quote"]) < 110 else item["quote"][:107] + "..."
            print(f"\n[{item['status']}] {item['file']}  ({item['score']:.0%} match)\n  \"{q}\"\n  cited: {', '.join(item['sources'])}")
    for item in all_unsourced[:25]:
        q = item["quote"] if len(item["quote"]) < 110 else item["quote"][:107] + "..."
        print(f"\n[UNSOURCED] {item['file']}\n  \"{q}\"")
    if len(all_unsourced) > 25:
        print(f"\n... and {len(all_unsourced) - 25} more unsourced quotes")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

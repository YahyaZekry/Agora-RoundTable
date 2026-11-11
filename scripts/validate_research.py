#!/usr/bin/env python3
"""Validate a coach's research/ folder: structure, links, index, and system map.

Checks, per research file (everything in research/ except _gaps.md and _system-map.md):
  ERROR  frontmatter missing, or missing domain / covers / answers / sources
  ERROR  `read_with` or [[see also]] link points at a file that does not exist
  ERROR  file not listed in persona.md's Deep-Dive Sources, or listed but missing
  ERROR  2+ research files but no _system-map.md, or a file absent from the map
  WARN   missing template sections (Frameworks, Decision Rules, ...)
  WARN   file over 4,000 words (split it) or under 150 words (too thin)
  WARN   quotes of 8+ words with no [src: ...] tag

Usage:
  python3 validate_research.py <persona-dir>
  python3 validate_research.py <persona-dir> --legacy    # files written before the template:
                                                         # frontmatter/map problems become WARN

Exit codes: 0 = no errors, 1 = errors found, 2 = bad arguments.
"""

import argparse
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ("domain", "covers", "answers", "sources")
REQUIRED_SECTIONS = ("Frameworks", "Decision Rules", "Stories & Numbers",
                     "Criticism & Limits", "See also", "No primary source in this folder")
MAX_WORDS, MIN_WORDS = 4000, 150
SPECIAL = {"_gaps.md", "_system-map.md"}
QUOTE_RE = re.compile(r'(?<!\w)["\u201c\u00ab](?=[\w$\[(])([^"\u201c\u201d\u00ab\u00bb\n]{15,}?)(?<=\S)["\u201d\u00bb]')
TAG_AFTER_RE = re.compile(r'^[^\[\n"\u201c\u201d\u00ab\u00bb]{0,100}?\[src:')


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        return None, text
    data, last = {}, None
    for line in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line.rstrip())
        if not line.strip():
            continue
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and last:
            data.setdefault(last, [])
            if not isinstance(data[last], list):
                data[last] = [data[last]] if data[last] else []
            data[last].append(item.group(1).strip())
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            last, val = kv.group(1), kv.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                data[last] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
            else:
                data[last] = val
    return data, text[m.end():]


def stem(name):
    return Path(name.replace("research/", "")).stem


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("persona_dir")
    ap.add_argument("--legacy", action="store_true",
                    help="research files predate the template: downgrade frontmatter/map errors to warnings")
    args = ap.parse_args()

    persona_dir = Path(args.persona_dir).expanduser()
    research = persona_dir / "research"
    if not research.is_dir():
        print(f"ERROR: {research} does not exist", file=sys.stderr)
        return 2
    files = sorted(f for f in research.glob("*.md") if f.name not in SPECIAL)
    if not files:
        print("ERROR: research/ has no topic files", file=sys.stderr)
        return 2

    errors, warnings = [], []
    soft = warnings if args.legacy else errors  # legacy downgrade target
    stems = {f.stem for f in files}

    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_frontmatter(text)
        label = f.name
        if meta is None:
            soft.append(f"{label}: no frontmatter (see references/research-template.md)")
            meta = {}
        else:
            for key in REQUIRED_KEYS:
                if not meta.get(key):
                    soft.append(f"{label}: frontmatter missing `{key}`")
            if meta.get("domain") and meta["domain"] != f.stem:
                warnings.append(f"{label}: frontmatter domain `{meta['domain']}` differs from file name")
        links = list(meta.get("read_with", [])) if isinstance(meta.get("read_with"), list) else []
        links += re.findall(r"\[\[([^\]]+)\]\]", body)
        for link in links:
            if stem(link) not in stems and link.strip() not in ("", "none"):
                errors.append(f"{label}: links to `{link}` but no such research file")
        for section in REQUIRED_SECTIONS:
            if not re.search(rf"^#{{1,4}}\s+.*{re.escape(section)}", body, flags=re.M | re.I):
                warnings.append(f"{label}: missing section `{section}`")
        words = len(body.split())
        if words > MAX_WORDS:
            warnings.append(f"{label}: {words} words, over {MAX_WORDS}; split by sub-topic and link with read_with")
        elif words < MIN_WORDS:
            warnings.append(f"{label}: only {words} words; too thin to stand alone")
        flat = " ".join(re.sub(r"```.*?```", "", body, flags=re.S).split())
        untagged = 0
        for m in QUOTE_RE.finditer(flat):
            if len(m.group(1).split()) >= 8 and not TAG_AFTER_RE.match(flat[m.end():m.end() + 130]):
                untagged += 1
        if untagged:
            warnings.append(f"{label}: {untagged} quote(s) of 8+ words with no [src: ...] tag")

    persona = persona_dir / "persona.md"
    if not persona.is_file():
        errors.append("persona.md missing")
    else:
        ptext = persona.read_text(encoding="utf-8", errors="replace")
        listed = {Path(p).stem for p in re.findall(r"research/([\w\-. ]+?\.md)", ptext)} - {"_gaps", "_system-map"}
        for s in sorted(stems - listed):
            errors.append(f"persona.md Deep-Dive Sources does not list research/{s}.md")
        for s in sorted(listed - stems):
            errors.append(f"persona.md lists research/{s}.md but the file does not exist")
        if len(stems) >= 2 and "_system-map" not in ptext:
            warnings.append("persona.md does not mention research/_system-map.md")

    smap = research / "_system-map.md"
    if len(files) >= 2:
        if not smap.is_file():
            soft.append("research/_system-map.md missing (needed once there are 2+ research files)")
        else:
            mtext = smap.read_text(encoding="utf-8", errors="replace")
            for s in sorted(stems):
                if s not in mtext:
                    soft.append(f"_system-map.md does not mention `{s}`")

    print(f"Validated {len(files)} research file(s) in {research}")
    for w in warnings:
        print(f"WARN   {w}")
    for e in errors:
        print(f"ERROR  {e}")
    if not errors:
        print("OK: no errors." + (f" {len(warnings)} warning(s)." if warnings else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

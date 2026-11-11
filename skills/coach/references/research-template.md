# Research file template

One file per **topic area** (not per source, not per count). Every file in
`DATA_DIR/<slug>/research/` except `_gaps.md` and `_system-map.md` follows this shape.
`scripts/validate_research.py` checks the frontmatter, the sections, the links, and the
index. `scripts/check_quotes.py` checks every tagged quote against its source.

## Splitting rules

- **Split by topic, merge by source.** If a transcript, a book and an inbox dossier all cover
  pricing, they go in ONE pricing file, each section tagged with its source. Never make a
  file per source for the same topic.
- Start a new file when the topic is a different *kind of question* a user would ask, or a
  different named system the person teaches.
- There is no cap on the number of files. There IS a cap on size: when a file passes
  ~4,000 words, split it by sub-topic and link the halves in `read_with`.
- A framework lives in exactly ONE file (its owner). Other files point to it with
  `see also`, they do not re-explain it.

## Quote convention (this is what makes quotes checkable)

Put the quote in double quotes and tag it immediately after with the source file:

```
"The reason Gym Launch has not been beaten is because we have better stats." [src: transcripts/scale-or-fail-12.md]
```

- `[src: ...]` is a path inside the persona folder (`transcripts/`, `inbox/`, `research/`).
- Several sources: `[src: transcripts/a.md; transcripts/b.md]`.
- Optional locator after `#`: `[src: transcripts/a.md#12:40]` (ignored by the checker).
- Web or book material you cannot store as a file: `[src: web:https://...]` or
  `[src: book:$100M Offers ch.4]`. These are reported as *uncheckable*, not as verified.
- Use `...` inside a quote to skip words. Each fragment is checked separately.
- A quote with no tag is treated as unsourced and warned about.

## The file

```markdown
---
domain: {domain-slug}                      # matches the file name
title: {Human title}
covers: {one line: what this file teaches}
answers:                                   # real questions a user would ask that this file serves
  - {question 1}
  - {question 2}
read_with: [{other-file-stem}, ...]        # files a good answer here usually needs too
sources:                                   # every source mined into this file
  - transcripts/{file}.md
  - inbox/{file}
source_type: primary | secondary | mixed   # secondary = built from someone else's summary
updated: {YYYY-MM-DD}
---

# {Title}

{2-3 sentences: where this topic sits in the person's overall system, and what it
depends on or feeds. Detail goes in `_system-map.md`; this is just the local pointer.}

## Frameworks

### {Framework name, in THEIR words}
- **What it is:** {definition as they teach it}
- **Steps / mechanism:** {numbered steps, or the causal mechanism}
- **When they use it:** {the situation that triggers it}
- **Numbers and thresholds:** {every concrete figure they attach: ratios, counts, dollars}
- **Origin story:** {the story they tell about where it came from, with its numbers}
- **In their words:** "{verbatim}" [src: ...]

## Decision Rules

How they actually decide. This is the part that makes a coach sound like the person and
not like a summary of the person. One rule per line, phrased as *when X, they do Y*.

- When {situation}, they {action}, because {their stated reason}. [src: ...]
- Before advising, they ask: {the diagnostic question}. [src: ...]
- They refuse / warn against: {the thing}, because {reason}. [src: ...]

## Stories & Numbers

{Case studies and examples they reach for, each with its real figures and who it
happened to.}

## Criticism & Limits

{What they get pushed on, how they respond, and where this advice stops applying.
Include tensions between this file's ideas and the rest of their system.}

## See also

- [[{other-file-stem}]] — {why: e.g. "the Value Equation, which this offer framework rests on"}

## No primary source in this folder

{Claims that are true to the person's reputation but came from no file in this folder.
Future answers hedge on these instead of quoting them. If none, write "None."}
```

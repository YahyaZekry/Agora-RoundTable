# System map template

`DATA_DIR/<slug>/research/_system-map.md` is the one file that shows how the person's whole
body of work fits together. Individual research files explain a topic; this file explains
how the topics depend on each other. It is what a coach reads first when the question is
broad ("how do I grow my business?", "what should I do with my life?") and what lets
a debate cover the whole system instead of one file.

Keep it under ~1,500 words. It points to files, it does not repeat them.

```markdown
---
domain: _system-map
title: {Full Name} — how the system fits together
covers: Order of operations, dependencies between frameworks, and which file owns what
updated: {YYYY-MM-DD}
---

# {Full Name} — system map

## The one-paragraph version

{How the person would explain their whole approach in under 100 words, in their terms.
Quote them if they have a line for it. [src: ...]}

## The sequence

{The order they teach things in, when there is one. Each step names the file that owns it.}

1. **{Stage}** — {one line}. Owner: `research/{file}.md` → {framework names}
2. **{Stage}** — {one line}. Owner: `research/{file}.md` → {framework names}

## Dependencies

{Which frameworks need which. Say what breaks if a prerequisite is missing.}

- {Framework A} is built on {Framework B}: `{file-a}` ← `{file-b}`
- {Framework C} only works after {condition}: `{file-c}`

## Root principles

{The few beliefs or capacities that every file grows from. Remove one and several
frameworks stop making sense.}

## Where to start, by situation

| If the user is... | Start with | Then |
|---|---|---|
| {situation} | `{file}` | `{file}` |

## Tensions in the system

{Places the person's own ideas pull against each other, and how they resolve it, or
that they never do. A coach should surface these honestly instead of smoothing them.}

## File index

| File | Owns | Read together with |
|---|---|---|
| `research/{file}.md` | {frameworks it is the owner of} | {file stems} |
```

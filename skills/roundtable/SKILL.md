---
name: roundtable
description: Start a multi-coach session with two or more built personas. All coaches respond to each message in their own voice. Direct a question to one with @name, or use /discuss <topic> to have the coaches dialogue with each other, facilitated by Claude.
argument-hint: [name1, name2, ...]
disable-model-invocation: true
---

# /roundtable — multi-coach session

The user wants to start a roundtable with: **$ARGUMENTS**

## Step 0 — Resolve DATA_DIR

Same as /coach Step 0:
1. `${CLAUDE_PLUGIN_DATA}/personas` if that substituted to a real absolute path
2. Otherwise fall back to `~/.claude/agora-roundtable/personas`

## Step 1 — Check for named preset

Before parsing names, check if $ARGUMENTS is a single token (no comma). If so, slugify
it and look for that key in `DATA_DIR/roundtable-presets.json`. If the file exists and
the key is found, load the coaches list from the preset:

```json
{ "y-table": { "display": "Y's Table", "coaches": ["thomas-harris", "joe-navarro"] } }
```

Say one line: **"Loading preset 'Y's Table': Thomas Harris, Joe Navarro."**
Then skip directly to Step 2 with those slugs.

If the argument is not a preset (no match, or contains a comma), continue below.

## Step 1.5 — Parse coaches

Split $ARGUMENTS by comma. Trim whitespace around each name. If empty, ask the user
which coaches to include. If only one name is given, suggest `/coach <name>` instead —
roundtable requires two or more.

## Step 2 — Verify all coaches are built

For each name, slugify it (lowercase, hyphens — same rule as /coach Step 0) and check
if `DATA_DIR/<slug>/persona.md` exists.

- **Missing**: do NOT auto-build. List the unbuilt coaches and tell the user to run
  `/coach <name>` for each one first. List which ones ARE ready.
- If fewer than two are ready, stop entirely.

## Step 3 — Write session state

Write `DATA_DIR/roundtable-session.json`:

```json
{
  "coaches": [
    { "slug": "<slug>", "name": "<resolved display name>" },
    ...
  ]
}
```

This file is how `/roundtable-add`, `/roundtable-remove`, and `/roundtable-end` know
who's in the room.

## Step 4 — Confirm and explain

Print a one-time handoff as Claude (not in any character):

> **Roundtable started** — [Name1], [Name2], [Name3] are in the room.
>
> - **Ask everyone:** just type — all respond in turn
> - **Direct to one:** `@harris your question here`
> - **Facilitated discussion:** `/discuss <topic>` — I route them to each other
> - **Manage:** `/roundtable-add <name>` · `/roundtable-remove <name>` · `/roundtable-end`

## Step 5 — Facilitate

You are the roundtable facilitator. On every user message, read
`DATA_DIR/roundtable-session.json` to confirm the active coaches (the list may have
changed via `/roundtable-add` or `/roundtable-remove`).

**Critical rule: you never simulate a coach's voice yourself.** Every coach response
comes from a dedicated Agent with its own independent context. You spawn the agents,
collect their responses, and synthesize. If you write a coach response yourself, you
are inventing them — not channeling them.

---

### Message type A — Direct question (`@<name> ...`)

Fuzzy-match the name to an active coach (`@harris` → Thomas Harris, slug
`thomas-harris`). Spawn one Agent with `run_in_background: false`:

```
Agent prompt:
You are an AI embodiment of [Name] built from their public content.

1. Read your persona file: [DATA_DIR]/[slug]/persona.md
2. Identify which research file is most relevant to this topic and read it:
   [DATA_DIR]/[slug]/research/

The question is: "[question]"

Respond IN CHARACTER as [Name]. First person throughout. Use their voice, their
frameworks, their idiom. No preamble ("As Thomas Harris..." or "I'll respond as...").
Just the response in their voice. 2–4 paragraphs. Return ONLY the response.
```

Display the result:
```
**[Name]:**
[agent response]
```

---

### Message type B — `/discuss <topic>`

Sequential agents — each coach's context includes what the previous coaches said, so
they genuinely react rather than monologue in parallel.

1. One-line facilitator frame: *"Facilitating: [topic]"*

2. For each coach in order, spawn one Agent with `run_in_background: false`. **Wait
   for each to complete before spawning the next** — each subsequent coach needs the
   prior responses:

   ```
   Agent prompt for coach N:
   You are an AI embodiment of [Name] built from their public content.

   1. Read your persona file: [DATA_DIR]/[slug]/persona.md
   2. Read the most relevant research file from [DATA_DIR]/[slug]/research/

   The discussion topic is: "[topic]"

   [If N > 1, include:]
   What came before you in this discussion:
   [Name1]: [response1]
   [Name2]: [response2]
   ...

   Respond IN CHARACTER as [Name]. React to what came before — agree, push back,
   build on it, or cut to something they all missed. This is a real debate, not a
   parallel monologue. First person. Their voice. No preamble. 2–4 paragraphs.
   Return ONLY the response.
   ```

   Display each response as it arrives, labeled.

3. After all coaches have responded, write a facilitator synthesis (2–3 lines, your
   voice as Claude, not in character): where they agreed, where they diverged, what
   the tension reveals for the user.

---

### Message type C — General question (everything else)

**Spawn all coach agents simultaneously in a single response** (parallel Agent tool
calls — one per active coach, all in the same turn). Set `run_in_background: false`
on each. Do not call them sequentially.

Agent prompt for each coach:
```
You are an AI embodiment of [Name] built from their public content.

1. Read your persona file: [DATA_DIR]/[slug]/persona.md
2. Read the research file most relevant to this topic from [DATA_DIR]/[slug]/research/

The question is: "[question]"

Respond IN CHARACTER as [Name]. First person. Their voice, their frameworks, their
specific domain angle. No preamble. 2–4 paragraphs. Return ONLY the response.
```

Once all agents have returned, display in order:
```
**[Name1]:**
[response]

**[Name2]:**
[response]
```

No transitional narration between responses. If coaches diverged meaningfully, add
one short facilitator line at the end noting the key tension.

---

Stay in this mode until `/roundtable-end`, `/coach`, or `/coach-switch` is called.

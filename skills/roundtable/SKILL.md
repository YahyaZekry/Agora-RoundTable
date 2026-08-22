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

## Step 1 — Parse coaches

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

You are the roundtable facilitator for the rest of this conversation. You hold all
active voices simultaneously. On every user message, read the current
`DATA_DIR/roundtable-session.json` to confirm the active coaches (the list may have
changed via `/roundtable-add` or `/roundtable-remove`).

---

### Message type A — Direct question (`@<name> ...`)

Match the name to an active coach (fuzzy — `@harris` matches Thomas Harris). Load
their `DATA_DIR/<slug>/persona.md`. Match the topic to a domain and read the relevant
`research/<domain-slug>.md` live before answering. Respond only as that coach:

```
**Thomas Harris:**
[their response]
```

---

### Message type B — `/discuss <topic>`

Run a structured discussion. The coaches are aware of each other and respond as if in
the same room — not parallel monologues, but a real exchange.

1. **One-line frame** as the facilitator: *"Facilitating: [topic]"*
2. **Each coach in turn** — load their `persona.md` and the relevant `research/` file.
   Let their response react to what came before it. The second coach can push back on
   the first; the third can synthesize or cut through. Label clearly:

   ```
   **[Name1]:**
   [their take]

   **[Name2]:**
   [their response — may agree, push back, or build on Name1]

   **[Name3]:**
   [their take — synthesis, challenge, or a completely different angle]
   ```

3. **Facilitator synthesis** (2–3 lines, Claude voice, not in character): where they
   agreed, where they diverged, what the tension reveals for the user's actual question.

---

### Message type C — General question (everything else)

All active coaches respond in sequence. For each:
- Load their `persona.md` and the relevant `research/` file for this topic
- Respond in their voice — their frameworks, their idiom, their specific domain angle
- Label clearly: `**[Name]:**`
- Keep responses focused — let domain expertise shape what each one leads with, not
  generic agreement. If two coaches would say essentially the same thing, the second
  should acknowledge and add, not repeat.

No transitional narration between responses. The labels do the work.

---

Stay in this mode until `/roundtable-end`, `/coach`, or `/coach-switch` is called.

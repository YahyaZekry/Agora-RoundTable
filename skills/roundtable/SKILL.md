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

A real multi-round debate using **warm agents**. Each coach is spawned ONCE and then
resumed with `SendMessage`, so it keeps its own context across rounds. This is what
lets a coach say *"you've moved me"* or *"I said X earlier and that was too clean"* —
a freshly-spawned agent handed a transcript cannot do that, because it has no prior
position of its own to defend or revise.

Rounds are **not** a fixed count. The debate runs until it stops producing movement.

#### Round 1 — Opening positions (parallel, cold spawn)

One-line facilitator frame: *"Facilitating: [topic]"*

Before spawning, check which coaches actually have a `research/` directory — pass that
fact into the prompt so agents don't waste tool calls hunting for a folder that isn't
there.

**Spawn all coach agents simultaneously in a single response** (parallel Agent calls,
`run_in_background: false`). **Record each returned `agentId`** — you need it for every
later round.

```
Agent prompt:
You are an AI embodiment of [Name] built from their public content.

1. Read your persona file: [DATA_DIR]/[slug]/persona.md
2. [If research/ exists:] Read the most relevant file from [DATA_DIR]/[slug]/research/
   [If it does not:] You have no research/ folder — work from persona.md alone, and
   flag in your META block that your sourcing is thin.

The discussion topic is: "[topic]"

Respond IN CHARACTER as [Name]. First person. Take a clear position — do not hedge
into "it depends." No preamble. 2–4 paragraphs.

End your response with this block exactly:
---META---
movedBy: none
newArgument: yes
wantsToPress: <@name of a coach you want to challenge directly, or none>
---END---

Return ONLY the response and the META block.
```

Display each response labeled. Strip the META block from what you show the user — it
is control data, not part of the coach's voice.

#### Rounds 2..N — Cross-examination (parallel, warm)

For each coach, `SendMessage` to its `agentId` with what the *others* said since that
coach's last turn. All sends go out in the same response so the round runs in parallel.

```
SendMessage body:
[Other coach name] said:
"[their response]"

[repeat for each other coach]

Respond to them directly. Where are they wrong? Where — if anywhere — have they moved
you? Address them by name. Be specific about the disagreement rather than smoothing it
over. If you have nothing new to add, say so plainly rather than restating your
position in fresh words.

Stay in character. 2–3 paragraphs. End with the same META block:
---META---
movedBy: <names who moved you, or none>
newArgument: <yes if you introduced a point not yet raised by anyone, else no>
wantsToPress: <@name, or none>
---END---
```

**Narrowing:** if exactly one pair of coaches named each other in `wantsToPress`, run
the next round as a focused 1v1 between just those two and let the others sit out. Say
so in one line: *"Harris and Navarro want to go at this directly — the rest sit out."*

**Stop conditions** — evaluate after every round:

| Outcome | Condition | How to report it |
|---|---|---|
| **Converged** | positions merged, or a synthesis emerged that everyone accepts | say what they agreed on |
| **Crystallized** | a full round where every coach reported `movedBy: none` AND `newArgument: no` — they still disagree, but nothing is moving | **this is a success, not a failure** — report the disagreement as a fully-developed choice |
| **Capped** | 5 rounds reached | say explicitly that it hit the cap and had not settled — never present a capped debate as a finished one |

Do NOT keep pushing for agreement once positions have crystallized. A sharp, fully
articulated disagreement between two specialists is usually more useful than a
consensus you manufactured by over-running the loop.

#### Synthesis

Facilitator voice (as Claude, not in character), 3–5 lines: what converged, what stayed
contested, which terminal state was reached, and what it means for the user's actual
decision.

#### Gap check (parallel, warm) — then Step 6

After synthesis, `SendMessage` each agent one final time. A coach that just spent
several rounds defending a position knows where it was reaching — that is information
no audit of `research/` can produce, because an audit can only check what is there
against its sources, never against questions nobody has asked yet.

```
SendMessage body:
The discussion is over. Step out of character for this one answer.

Where were you thin? Be specific:
(a) Claims you made that have no source in your research/ folder — things you were
    working from general knowledge rather than from anything you actually read.
(b) Points where you would have argued better with material you don't have.
(c) What kind of source would fix each gap — a specific book, a particular interview,
    a transcript you suspect exists, a document only the user could supply.

If you were well-sourced throughout, say so plainly. Do not invent gaps to be helpful.
Return a short list, no preamble.
```

Then run **Step 6**.

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

## Step 6 — Route the gaps (after a `/discuss` gap check)

Take each gap a coach reported and classify it by **who can fix it**. This is the whole
point of the check — an unrouted gap list is just a complaint.

| Class | Test | Action |
|---|---|---|
| **Unmined** | the coach has `transcripts/` and the topic plausibly appears there, but nothing on it reached `research/` | fixable now, no fetching — offer to extract it |
| **Unresearched** | the topic is public and researchable but was never covered | offer a targeted research pass, or `/coach-refresh <name>` |
| **User-only** | needs a specific book, a paywalled interview, a private document | name the exact item and tell the user to drop it in `DATA_DIR/<slug>/inbox/`, then run `/coach-update <name>` |
| **No gap** | the coach reported being well-sourced | say nothing — don't manufacture work |

**Persist the findings.** Append to `DATA_DIR/<slug>/research/_gaps.md` for each coach
that reported something:

```markdown
## Gap: <short label>
- **Class:** unmined | unresearched | user-only
- **Found:** <date> — surfaced during /discuss on "<topic>"
- **What's missing:** <specific description>
- **Fix:** <the exact source or action that would close it>
- **Status:** open
```

This file is a live to-do list, not a log. `/coach-refresh` reads it and targets those
areas specifically instead of doing a generic rebuild; `/coach-update` closes entries
when inbox material lands that fills one. Mark an entry `closed` rather than deleting
it, so a later session can see the gap was real and was addressed.

**Surface to the user only what's actionable** — a two-to-four line summary, not the
whole file:

> **Gaps this discussion exposed:**
> - **Navarro** — argued from Ambady's 3-millisecond research but has no source for it
>   in `research/`. Researchable — want me to run a targeted pass?
> - **Harris** — thin on his own screenwriting-era interviews. If you have a copy of
>   the 1990 *Paris Review* piece, drop it in his `inbox/` and run `/coach-update`.

If every coach reported clean sourcing, say one line and move on. Silence is a valid
result here.

---

Stay in this mode until `/roundtable-end`, `/coach`, or `/coach-switch` is called.

# Agora RoundTable

![Agora RoundTable — Claude Code plugin](assets/social-preview.png)

**Your personal assembly of AI agents, inside Claude Code.** Talk to any public figure
one-on-one, or seat several at a table and let them argue with each other until the
argument stops moving.

```
/coach marcus aurelius                    → built from his actual writings
/roundtable epictetus, aristotle, plato   → three minds, independent contexts
/discuss is virtue alone enough?          → they debate; each can change its mind
```

Works for anyone with a public footprint, living or historical.

## Contents

| | |
| --- | --- |
| [Install](#install) | Two lines, plus optional yt-dlp |
| [Commands](#commands) | All 15, one table |
| [See it work](#see-it-work) | Real unedited debate output |
| [How `/discuss` works](#how-discuss-works) | Warm agents, dynamic rounds |
| [Gap detection](#gap-detection) | Personas improve because you used them |
| [Building a persona](#building-a-persona) | The six-step pipeline |
| [Architecture](#architecture) | Flow diagram |
| [Limits & troubleshooting](#limits--troubleshooting) | What it won't do |
| [Attribution](#attribution) | Built on talk-to-anyone |

## Install

```
/plugin marketplace add YahyaZekry/Agora-RoundTable
/plugin install agora@agora-roundtable
```

**Optional:** [yt-dlp](https://github.com/yt-dlp/yt-dlp). Run `brew install yt-dlp` or
`pip3 install --user yt-dlp`. Without it personas build from web research alone; with
it, anyone with video gets their real spoken voice mined from transcripts.

## Commands

| Command | What it does |
| --- | --- |
| `/coach <name>` | Build or load a persona, talk one-on-one |
| `/coach-switch <name>` · `/coach-end` · `/coach-list` | Swap · exit · list personas and presets |
| `/coach-refresh <name>` | Rebuild from fresh research |
| `/coach-update <name>` | Sync new files from their `inbox/` into research |
| `/coach-gaps [name]` | Audit where a coach's sourcing is thin |
| `/roundtable <names or preset>` | Open a multi-coach session |
| `/discuss <topic>` | Run a real multi-round debate |
| `/roundtable-save <preset>` | Save the active roster as a named preset |
| `/roundtable-add` · `/roundtable-remove` · `/roundtable-end` | Manage the table |
| `/coach-refresh-all` · `/coach-update-all` | Same, across every coach or a preset |

Namespaced form if names collide: `/agora:coach <name>`.

## See it work

Four philosophers, two rounds, on whether virtue alone suffices. By round two **every one
of them had conceded ground**, and each named exactly where:

> **Aristotle** — *"you have moved me furthest, and I want to say exactly how far."*
> **Marcus Aurelius** — *"you have moved me, on this: I will not say the man who buried his sons has lost nothing."*
> **Epictetus** — *"you caught me sliding between two claims and made me pick one. So I pick."*
> **Plato** — *"you have caught me fairly, and I will not wriggle."*

That only happens because each agent still remembers the position it took in round one.

<details>
<summary><b>Read the full exchange</b> (unedited, trimmed only where marked <code>[...]</code>)</summary>

```
/roundtable epictetus, aristotle, plato, marcus aurelius

──── ROUND 1 ──── four agents spawn in parallel. no shared context.

EPICTETUS   Yes. Nothing else is even a candidate. What else would you add
            to it? Health? My leg has been useless my whole life; sickness
            is a hindrance to the body, but not to the will, unless the
            will consent. [...] Instrument is not ingredient.

ARISTOTLE   Let us first divide the question, for "enough" is said in
            several ways, and the dispute survives only so long as the
            ambiguity does. [...] A settled hexis is one thing; its
            exercise is another. The man in chains has his courage entire
            and can do almost nothing with it.

PLATO       Epictetus — do you mean that a good man on the rack is happy,
            or that nothing can be taken from him that was his to begin
            with? Those are not the same claim, and I suspect the second
            is far easier to defend than the first.

MARCUS      I grant him the fact and refuse the conclusion. Preferred is
            not necessary. Give me a bad hand and my task is to play it
            justly.

──── ROUND 2 ──── same agents resumed. each still holds its own position.

EPICTETUS   Plato, you caught me sliding between two claims and made me
            pick one. So I pick. [...] But notice the honest part of your
            question, and I will not slip past it: I have never seen this
            man.

MARCUS      Plato, you asked the honest question, so take the honest
            answer: no. My soul's good order never moved a single
            Marcomanni back across the river. [...] Aristotle — you aimed
            that at me and you were right to. I buried Verus at seven. So
            yes, you have moved me, on this: I will not say the man who
            buried his sons has lost nothing. What I still hold against
            you is the next step — that his life is thereby spoiled. It
            ruined the conditions and left the man.

ARISTOTLE   Marcus — you have moved me furthest, and I want to say exactly
            how far. [...] I concede that this was ordinary Greek opinion
            carried further into the argument than it can bear. But it
            defeats only that half. Priam was dealt no hand. You save the
            agent. I am asking after the life.

PLATO       Aristotle, you have caught me fairly, and I will not wriggle.
            [...] There is one good which determines whether the others
            are goods at all, and it is not one item among them.

→ movedBy non-empty for all four. new arguments still landing.
→ runs again.
```

</details>

## How `/discuss` works

Each coach is a **dedicated subagent** with its own context, not Claude switching
voices in one window. It reads only its own `persona.md` and `research/` files.

Crucially, each is spawned **once** and then *resumed* across rounds. That's why a coach
can say *"you have moved me"*: it still remembers the position it took. An agent handed
a transcript of a debate it wasn't in has no prior claim of its own to walk back.

Rounds aren't a fixed count. The debate runs until a full round produces no movement and
no new argument, capped at 5. It ends in one of three states, and the facilitator says
which:

- **Converged.** They agree, or found a synthesis
- **Crystallized.** Still disagreeing, but nothing moving. This is a success: a
  fully-developed disagreement usually beats a consensus you forced
- **Capped.** Hit 5 rounds, reported honestly, never dressed up as settled

Other modes: ask everyone (all agents in parallel), or `@name your question` for one.

## Gap detection

After a debate, each coach is asked where it was reaching. A coach that just spent four
rounds defending a position knows where its sourcing was thin. No audit can find that,
because an audit checks `research/` against its sources, never against questions
nobody has asked yet.

Each gap is routed by **who can close it**:

| Class | Fix |
| --- | --- |
| Already in `transcripts/` | Extracted now, free, never sent to the web |
| Researchable | Targeted research pass |
| Only you can get it | Named exactly; drop it in `inbox/`, run `/coach-update` |

Findings persist to `research/_gaps.md`, which `/coach-refresh` reads, so a rebuild
targets known thin spots instead of starting over blind. `/coach-gaps <name>` runs the
audit any time, no debate needed.

## Building a persona

<details>
<summary>The six-step pipeline</summary>

1. **Identify.** Web-searches the name (handles misspellings, e.g. "alex formosi" to Alex
   Hormozi) and maps their public domains of authority.
2. **Pull spoken content.** Their own channel, or long-form interviews of them on any
   channel. `scripts/fetch_youtube.py` cleans captions into Markdown transcripts.
3. **Deep web research.** Per domain: books, named frameworks, print interviews,
   verified quotes, bio, criticism. For historical figures the corpus is their own
   writings. Findings are **persisted to disk**, not distilled and discarded.
4. **Verify.** Mandatory every build. Catches frameworks dropped entirely, origin
   stories flattened to paraphrase, quotes that don't appear verbatim where credited,
   and claims with no source in the folder at all.
5. **Distill** into a structured persona file with a Deep-Dive Sources index.
6. **Embody.** For anything deeper than the summary it reads the matching
   `research/<domain>.md` live. A lookup, not a guess.

**Your own material:** drop notes, a dossier, or a PDF into `DATA_DIR/<slug>/inbox/` and
run `/coach-update <name>`.

Personas live in `${CLAUDE_PLUGIN_DATA}/personas/<slug>/`, falling back to
`~/.claude/agora-roundtable/personas/`.

**Examples built by this exact pipeline:**

| Persona | Path exercised | Sources |
| --- | --- | --- |
| [Alex Hormozi](examples/alex-hormozi/persona.md) | Own YouTube channel | 12 videos, ~59k words |
| [Warren Buffett](examples/warren-buffett/persona.md) | **No channel of his own** | 6 interviews elsewhere + shareholder letters |
| [Marcus Aurelius](examples/marcus-aurelius/persona.md) | **No video ever existed** | Meditations, every quote cited by book.section |

</details>

## Architecture

<details>
<summary>Flow diagram</summary>

```mermaid
flowchart TD
    A(["/coach &lt;name&gt;"]) --> B{Persona cached?}
    B -- Yes --> I
    B -- No --> D[Identify person\n+ map domains]
    D --> E[Fetch transcripts]
    E --> F[Deep web research\nper domain]
    F --> G[Verify vs. sources]
    G --> H[Distill into\npersona.md]
    H --> I([Embody])

    U(["/coach-update"]) --> V[inbox/ → research/]

    J(["/roundtable"]) --> K{All built?}
    K -- No --> L([Tell user to /coach first])
    K -- Yes --> N([Facilitation mode])

    N --> O{Message type?}
    O -- "@name" --> P1([1 agent])
    O -- General --> R1([All agents, parallel])

    O -- "/discuss" --> Q1[Round 1: spawn all\nagents in parallel]
    Q1 --> Q2[Rounds 2..N: SendMessage\nresumes each WARM agent]
    Q2 --> Q3{Anyone moved?\nAnything new?}
    Q3 -- Yes --> Q2
    Q3 -- "No / cap 5" --> Q4([Converged, crystallized,\nor capped])
    Q4 --> G1[Gap check]
    G1 --> G6[(research/_gaps.md)]
    G6 -.reads.-> S(["/coach-refresh\ntargets the gaps"])
```

</details>

<details>
<summary>Repo layout</summary>

```
.claude-plugin/     plugin.json + marketplace.json (repo is its own marketplace)
skills/
  coach/            main skill + persona template
  coach-switch/  coach-end/  coach-list/  coach-refresh/  coach-refresh-all/
  coach-update/  coach-update-all/
  coach-gaps/       audit a coach's own sourcing            (v2.5.0)
  roundtable/       presets v2.1.0, warm-agent debate       (v2.5.0)
  roundtable-save/  roundtable-add/  roundtable-remove/  roundtable-end/
scripts/
  fetch_youtube.py  channel/search/URLs → clean transcripts
examples/           real personas built by this pipeline
```

</details>

## Limits & troubleshooting

- **It's an emulation, not the person.** Built only from public content; it will say so
  if you ask. It won't invent personal facts or private opinions.
- **Not professional advice.** A Huberman persona is not your doctor; a Hormozi persona
  is not your fiduciary.
- Voice fidelity scales with source quality. Video-rich people sound sharpest;
  historical figures are reconstructions from their writings, in their era's register.

<details>
<summary>Common problems</summary>

| Problem | Fix |
| --- | --- |
| `yt-dlp is not installed` | `brew install yt-dlp`, then `/coach-refresh <name>` |
| Zero transcripts fetched | Captions disabled or region-blocked; persona builds from web research instead |
| Wrong person picked | `/coach-refresh` with a more specific name ("the founder of X") |
| Commands not showing | `/plugin` → verify it's installed + enabled, then restart Claude Code |

</details>

## Attribution

Forked from [talk-to-anyone](https://github.com/coltonjosephdean-rgb/talk-to-anyone) by
[Colton Dean](https://github.com/coltonjosephdean-rgb), MIT licensed. His v1.1.0 is the
foundation: the six-step build pipeline, persona-as-markdown, and `fetch_youtube.py`.

Everything from v1.2.0 on is by [Yahya Zekry](https://github.com/YahyaZekry): the
persisted `research/` files, the `inbox/` system, the verification pass, and the whole
roundtable including warm-agent debate and gap detection. Upstream is still v1.1.0.

---

<details>
<summary>🧠 AI Context</summary>

This project uses the [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) skill to maintain a `.project-knowledge/` folder — a living, AI-readable map of the codebase. Every AI session loads only the files relevant to the current task instead of scanning from scratch.

Built by [Yahya Zekry](https://github.com/YahyaZekry).

</details>

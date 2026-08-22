# Agora RoundTable

![Agora RoundTable — Claude Code plugin](assets/social-preview.png)

**Your personal assembly of AI agents, inside Claude Code.** Talk to any public figure
one-on-one — or open a roundtable and have multiple minds respond to you simultaneously,
debate each other, and synthesize their expertise around your question.

```
/coach thomas harris         → talk to the author of Red Dragon one-on-one
/roundtable thomas harris, gillian flynn, dennis lehane
                             → open a roundtable of three minds at once
/discuss whose POV for the opening scene?
                             → they debate it; Claude synthesizes
```

Build a persona once from their real interviews, books, transcripts, and writings.
Then summon them any time — solo or together.

## Install

```
/plugin marketplace add YahyaZekry/Agora-RoundTable
/plugin install agora-roundtable@agora-roundtable
```

**Optional (recommended):** [yt-dlp](https://github.com/yt-dlp/yt-dlp) for transcript
pulling — `brew install yt-dlp` or `pip3 install --user yt-dlp`. Without it, personas
build from web research alone; with it, people with video content get their real
spoken voice mined from transcripts.

## Commands

| Command | What it does |
| --- | --- |
| `/coach <name>` | Build (or load) a persona and talk to them one-on-one |
| `/coach-switch <name>` | Swap coaches mid-conversation |
| `/coach-end` | Back to normal Claude |
| `/coach-list` | Show every persona saved on this machine |
| `/coach-refresh <name>` | Rebuild a persona from fresh research |
| `/roundtable <name1>, <name2>, ...` | Open a roundtable with multiple coaches |
| `/roundtable-add <name>` | Add a coach to an active roundtable |
| `/roundtable-remove <name>` | Remove a coach from the roundtable |
| `/roundtable-end` | Close the roundtable, back to normal Claude |

If the short names collide with another plugin, use the namespaced form:
`/agora-roundtable:coach <name>`.

## How it works

### Building a persona

1. **Identify** — web-searches the name (handles misspellings: "alex formosi" →
   Alex Hormozi) and maps their public domains of authority.
2. **Pull spoken content** — when any exists: their own channel's popular videos, or
   long-form interviews/podcasts/keynotes OF them on any channel (`--search` mode).
   `scripts/fetch_youtube.py` downloads captions with yt-dlp and cleans them into
   Markdown transcripts.
3. **Deep web research** — every build, run per domain: books and their core ideas,
   named frameworks, print interviews, verified quotes, bio, common criticism.
   For historical figures the corpus is their own writings — letters, essays, speeches.
   Findings are **persisted to disk** per domain, not just distilled and discarded.
4. **Verify** — mandatory every build: checks research against the actual transcripts
   and sources fresh. Catches frameworks dropped entirely, origin stories flattened to
   generic paraphrase, and quotes that don't appear verbatim where credited.
5. **Distill** — merges everything into a structured persona file: identity, voice,
   core beliefs (with verbatim quotes), named frameworks, coaching style, signature
   quotes, and a Deep-Dive Sources index.
6. **Check `inbox/`** — every invocation, cache hit or not: anything you've dropped in
   yourself (notes, a dossier, a PDF) gets extracted into the matching
   `research/<domain>.md` and tracked in `inbox/_sync-status.md`.
7. **Embody** — Claude speaks as them until you end or switch. For anything deeper than
   the persona summary, it reads the matching `research/<domain>.md` live before
   answering — a lookup, not a guess.

Personas live in `${CLAUDE_PLUGIN_DATA}/personas/<slug>/` (survives plugin updates),
falling back to `~/.claude/agora-roundtable/personas/`.

### Roundtable mode

Run multiple already-built personas simultaneously. Three message modes:

- **Ask everyone** — type normally; all coaches respond in sequence, each from their
  domain expertise.
- **Direct to one** — `@harris what do you think about the opening scene?` — only
  that coach responds.
- **Facilitated discussion** — `/discuss <topic>` — Claude routes the topic through
  each coach, lets them react to each other, then synthesizes agreements and tensions.

```
/roundtable thomas harris, gillian flynn, dennis lehane

You: /discuss whose POV should the first scene use?

Thomas Harris:
[his take — the profiler's entry point]

Gillian Flynn:
[her response — may push back on Harris]

Dennis Lehane:
[synthesis or a third angle]

[Facilitator: where they agreed, where they diverged, what it means for your decision]
```

Coaches must be built first with `/coach <name>`. The active roster persists in
`DATA_DIR/roundtable-session.json` so `/roundtable-add` and `/roundtable-remove`
can modify it mid-conversation.

## What it feels like

Real output from a built persona, not a mockup — `/coach alex hormozi`, first message:

> What's up, man. Rock and roll — let's do this.
>
> So here's how this usually goes: you tell me what you're working on, and then I'm
> gonna ask you a bunch of questions, because I always fix things from back to front —
> the thing you sell, how you sell it, who you sell it to, and how they find out about
> you. Right? And most of the time the constraint isn't the one people think it is.
>
> So — what do you do, how much money do you make, and what's the problem right now?

That opener isn't scripted. It's his actual diagnostic pattern, mined from 12 of his
videos.

## Example personas (built by this exact pipeline)

| Persona | Path exercised | Sources |
| --- | --- | --- |
| [Alex Hormozi](examples/alex-hormozi/persona.md) | Own YouTube channel | 12 videos, ~59k transcript words |
| [Warren Buffett](examples/warren-buffett/persona.md) | **No channel of his own** | 6 interviews from other channels (~69k words) + his shareholder letters |
| [Marcus Aurelius](examples/marcus-aurelius/persona.md) | **No video ever existed** | Meditations full text, every quote cited by book.section |

## Attribution

Based on [talk-to-anyone](https://github.com/coltonjosephdean-rgb/talk-to-anyone) by
[Colton Dean](https://github.com/coltonjosephdean-rgb), licensed MIT. The core
persona-building pipeline (Steps 1–6, the verification pass, inbox extraction) is his
original work. The roundtable feature and ongoing development are by
[Yahya Zekry](https://github.com/YahyaZekry).

## Honest limits

- **It's an emulation, not the person.** Built only from public content; it will say so
  if you ask. It won't invent personal facts or private opinions.
- **Not professional advice.** A Huberman persona repeating his public protocols is not
  your doctor; a Hormozi persona is not your fiduciary.
- Voice fidelity scales with source quality: video-rich people sound sharpest,
  web-only builds lean on written quotes, and historical figures are reconstructions
  from their writings in their era's register.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `yt-dlp is not installed` | `brew install yt-dlp` (or `pip3 install --user yt-dlp`), then `/coach-refresh <name>` |
| Zero transcripts fetched | Channel may have captions disabled or region-blocked; persona builds from web research instead |
| Wrong person picked | `/coach-refresh` with a more specific name ("the podcaster", "the founder of X") |
| Commands not showing | `/plugin` → verify agora-roundtable is installed + enabled, then restart Claude Code |

## Repo layout

```
.claude-plugin/
  plugin.json          # plugin manifest
  marketplace.json     # this repo doubles as its own marketplace
skills/
  coach/               # main skill + persona template
  coach-switch/  coach-end/  coach-list/  coach-refresh/
  roundtable/          # multi-coach session
  roundtable-add/  roundtable-remove/  roundtable-end/
scripts/
  fetch_youtube.py     # channel/search/URLs → long-form videos → clean transcripts
examples/
  alex-hormozi/        # real persona built by this pipeline
```

---

<details>
<summary>🧠 AI Context</summary>

This project uses the [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) skill to maintain a `.project-knowledge/` folder — a living, AI-readable map of the codebase. Every AI session loads only the files relevant to the current task instead of scanning from scratch.

Built by [Yahya Zekry](https://github.com/YahyaZekry).

</details>

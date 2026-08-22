# Talk to Anyone

![Talk to Anyone — Claude Code plugin](assets/social-preview.png)

**Turn any person on earth into your personal coach, inside Claude Code.** Type `/coach` and a name. It researches them — their real interviews, books, transcripts, writings — and then you're talking to them.

```
/coach alex hormozi     → business coaching from Alex Hormozi
/coach andrew huberman  → health protocols from Andrew Huberman
/coach warren buffett   → no YouTube channel needed — interviews + shareholder letters
/coach marcus aurelius  → no video at all — built from his actual writings
```

When you name a person, the plugin researches them across the web — interviews,
books, articles, documented quotes — and, when they have video content anywhere on
YouTube (their own channel or interviews on other people's), pulls **real transcripts
of them speaking** (no API keys). Everything gets distilled into a persona file: their
voice, beliefs, named frameworks, signature phrases, and how they actually give
advice. Then Claude *becomes* them for the rest of the conversation — answers come in
their voice, grounded in what they actually teach. Works for anyone with a public
footprint, living or historical.

Personas are cached locally, so the first `/coach alex hormozi` takes a couple of
minutes and every one after loads instantly.

## Install

```
/plugin marketplace add YahyaZekry/agora-roundtable
/plugin install agora-roundtable@agora-roundtable
```

**Optional (recommended):** [yt-dlp](https://github.com/yt-dlp/yt-dlp) for transcript
pulling — `brew install yt-dlp` or `pip3 install --user yt-dlp`. Without it, personas
build from web research alone; with it, people with video content get their real
spoken voice mined from transcripts.

## Commands

| Command | What it does |
| --- | --- |
| `/coach <name>` | Build (or load) the persona and start talking to them |
| `/coach-switch <name>` | Swap coaches mid-conversation |
| `/coach-end` | Back to normal Claude |
| `/coach-list` | Show every coach saved on this machine |
| `/coach-refresh <name>` | Rebuild a persona from fresh research |
| `/roundtable <name1>, <name2>, ...` | Start a session with multiple coaches simultaneously |
| `/roundtable-add <name>` | Add a coach to an active roundtable |
| `/roundtable-remove <name>` | Remove a coach from an active roundtable |
| `/roundtable-end` | End the roundtable, back to normal Claude |

If the short names collide with another plugin, use the namespaced form:
`/agora-roundtable:coach <name>`.

## How it works

1. **Identify** — web-searches the name (handles misspellings: "alex formosi" →
   Alex Hormozi) and maps their public footprint.
2. **Pull spoken content** — when any exists: their own channel's popular videos, or
   long-form interviews/podcasts/keynotes OF them on any channel (`--search` mode).
   `scripts/fetch_youtube.py` downloads captions with yt-dlp (manual subs preferred,
   auto-captions fallback) and cleans them into Markdown transcripts (with a frontmatter header).
3. **Deep web research** — every build, run per domain the person's actually known
   for (a marketing guru who's also a content creator gets two research passes, not
   one blended sweep): books and their core ideas, named frameworks, print interviews
   and profiles, verified quotes, bio, common criticism. For people with little or no
   video this is the primary source; for historical figures the corpus is their own
   writings — letters, essays, speeches. Findings are **persisted to disk** per domain,
   not just distilled and discarded.
4. **Verify** — every build, mandatory: checks the just-written research against the
   actual transcripts and sources fresh, not against its own summary. Catches named
   frameworks dropped entirely, origin stories flattened to generic paraphrase, and
   quotes that don't actually appear verbatim where credited — real failure modes,
   caught in practice, not hypothetical.
5. **Distill** — Claude merges both streams into a structured persona file: identity,
   voice & delivery, core beliefs (with verbatim quotes), named frameworks with their
   actual steps, coaching style, signature quotes, a Deep-Dive Sources index, and
   embodiment rules.
6. **Check `inbox/`** — every invocation, cache hit or not: anything you've dropped in
   yourself (notes, a dossier, a PDF) gets extracted into the matching
   `research/<domain>.md`, same as step 3's findings — a manifest
   (`inbox/_sync-status.md`) tracks what's already been folded in so nothing gets
   re-processed every time.
7. **Embody** — Claude speaks as them until you end or switch. Advice is grounded in
   their real content; when it extrapolates beyond it, it says so in their voice. For
   anything deeper than the persona file's compressed summary, Claude matches the
   question's topic to a domain and reads that `research/<domain>.md` live — a
   lookup, not a guess.

Personas live in `${CLAUDE_PLUGIN_DATA}/personas/<slug>/` (survives plugin updates),
falling back to `~/.claude/agora-roundtable/personas/`. Each contains `persona.md`,
`videos.json`, the raw `transcripts/` (mined into `research/`, then archival),
`research/` (one flat file per domain, the persisted depth behind the summary), and
`inbox/` — drop your own files there any time; they'll be folded in next `/coach` call.

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

## Roundtable mode

Run multiple coaches simultaneously and have them respond to your questions in their
own voice — or use `/discuss <topic>` to have them talk *to each other*, facilitated
by Claude.

```
/roundtable thomas harris, gillian flynn, dennis lehane
```

Three modes inside a roundtable session:

- **Ask everyone** — type normally; all coaches respond in sequence, each from their
  domain expertise. Harris on character psychology, Flynn on what's hidden, Lehane on
  structure.
- **Direct to one** — `@harris what do you think about Y's opening scene?` — only
  that coach responds.
- **Facilitated discussion** — `/discuss whose POV should the first scene use?` —
  Claude routes the question through each coach, lets them react to each other, then
  synthesizes where they agreed and where they diverged.

Coaches must be built first with `/coach <name>`. The roundtable session persists the
active roster in `DATA_DIR/roundtable-session.json` so `/roundtable-add` and
`/roundtable-remove` can modify it mid-conversation.

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
| Commands not showing | `/plugin` → verify talk-to-anyone is installed + enabled, then restart Claude Code |

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

Built by [Yahya Zekry](https://github.com/YahyaZekry/claude-code-skills).

</details>

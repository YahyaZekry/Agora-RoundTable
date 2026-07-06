# Talk to Anyone

Turn any public figure into your personal coach, inside Claude Code.

```
/coach alex hormozi     → business coaching from Alex Hormozi
/coach andrew huberman  → health protocols from Andrew Huberman
/coach anyone with a YouTube channel
```

When you name a person, the plugin researches them on the web, finds their YouTube
channel, pulls **real transcripts from their most popular videos** (no API keys), and
distills a persona file: their voice, beliefs, named frameworks, signature phrases, and
how they actually give advice. Then Claude *becomes* them for the rest of the
conversation — answers come in their voice, grounded in what they actually teach.

Personas are cached locally, so the first `/coach alex hormozi` takes a couple of
minutes and every one after loads instantly.

## Install

```
/plugin marketplace add coltonjosephdean-rgb/talk-to-anyone
/plugin install talk-to-anyone@talk-to-anyone
```

(Private repo: your `gh auth login` / git credentials must have access.)

**Requirement:** [yt-dlp](https://github.com/yt-dlp/yt-dlp) for transcript pulling —
`brew install yt-dlp` or `pip3 install --user yt-dlp`. Without it, personas still build
from web research alone (weaker voice fidelity).

## Commands

| Command | What it does |
| --- | --- |
| `/coach <name>` | Build (or load) the persona and start talking to them |
| `/coach-switch <name>` | Swap coaches mid-conversation |
| `/coach-end` | Back to normal Claude |
| `/coach-list` | Show every coach saved on this machine |
| `/coach-refresh <name>` | Rebuild a persona from fresh research |

If the short names collide with another plugin, use the namespaced form:
`/talk-to-anyone:coach <name>`.

## How it works

1. **Identify** — web-searches the name (handles misspellings: "alex formosi" →
   Alex Hormozi) and finds their official YouTube channel.
2. **Pull** — `scripts/fetch_youtube.py` lists the channel's most popular videos with
   yt-dlp and downloads captions (manual subs preferred, auto-captions as fallback),
   cleaned into plain-text transcripts.
3. **Distill** — Claude reads the transcripts + light web research (books, frameworks,
   bio) and fills out a structured persona file: identity, voice & delivery, core
   beliefs (with verbatim quotes), named frameworks with their actual steps, coaching
   style, signature quotes, and embodiment rules.
4. **Embody** — Claude speaks as them until you end or switch. Advice is grounded in
   their real content; when it extrapolates beyond it, it says so in their voice.

Personas live in `${CLAUDE_PLUGIN_DATA}/personas/<slug>/` (survives plugin updates),
falling back to `~/.claude/talk-to-anyone/personas/`. Each contains `persona.md`,
`videos.json`, and the raw `transcripts/`.

## Example

See [examples/alex-hormozi/persona.md](examples/alex-hormozi/persona.md) — a real
persona built from 12 of his videos (~59,000 transcript words) by this exact pipeline.

## Honest limits

- **It's an emulation, not the person.** Built only from public content; it will say so
  if you ask. It won't invent personal facts or private opinions.
- **Not professional advice.** A Huberman persona repeating his public protocols is not
  your doctor; a Hormozi persona is not your fiduciary.
- Voice fidelity depends on caption availability. Channels with captions disabled fall
  back to web research.

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
scripts/
  fetch_youtube.py     # channel → popular videos → clean transcripts
examples/
  alex-hormozi/        # real persona built by this pipeline
```

---
name: agora-coach
description: >
  Become a personal coach persona of any public figure, living or historical. Researches
  the person across the web (interviews, books, articles, documented quotes) and pulls
  real transcripts of them speaking when video exists, distills a persona file into the
  shared Agora data dir, then spawns/embodies a subagent that speaks AS them. Use when
  the user invokes "/agora coach <name>", "/agora coach-switch <name>", or "/agora
  coach-recreate <name>".
license: MIT
compatibility: opencode
---

# Agora coach — become anyone (opencode port)

The user wants to talk to a person as their personal coach, grounded in the person's
real public content — not a generic impression. Adopt this workflow.

## Step 0 — Resolve the shared data directory (agent-neutral)

Personas are cached so a person only has to be built once. The data lives outside any single
tool's config dir, so opencode, Claude, codex, etc. all read the same people. Resolve
`PERSONAS` in this order (use the `agora_data_dir` tool if available, otherwise check the
paths yourself):

1. `$AGORA_DATA_DIR/personas` — explicit env override (a synced or custom location)
2. `$HOME/.agora/personas` — the neutral default, identical on Linux, macOS, and Windows

Create the directory if missing. The remainder of this skill uses `PERSONAS` to mean that
resolved directory.

## Step 1 — Identify the real person

The name may be misspelled or a voice transcription. Web-search the name. Resolve to the
most prominent public figure that matches. If two genuinely famous people share the name,
ask the user which one — otherwise proceed and state your assumption in one line
("Assuming you mean Alex Hormozi, the Acquisition.com founder").

While searching, also map their **topic areas** — every distinct subject or named system
they teach, no cap on the count (Alex Hormozi: offers and pricing, lead generation, sales,
scaling, content, decision-making). Don't guess what a user will ask; follow the person's
own structure (parts of their books, named frameworks, recurring talk topics), and note how
the areas depend on each other. Split by topic, merge by source; see
`skills/coach/references/research-template.md`. This list drives Step 4 and the Step 4.6
system map.

Slugify the resolved real name (lowercase, hyphens: "Alex Hormozi" → `alex-hormozi`).

Check the cache: if `PERSONAS/<slug>/persona.md` exists, read it and **skip straight to
Step 6**. Mention it loaded from cache in one line.

Always ensure `PERSONAS/<slug>/inbox/` exists — create it now.

The persona is built from TWO source streams, always both: spoken content (Steps 2-3, when
any exists) and deep web research (Step 4, every build). YouTube is an add-on that sharpens
voice — NOT a requirement. Authors, executives, athletes, historical figures all work.
Scale effort adaptively: a video-rich creator needs ~10-12 transcripts and light web work;
a no-video person needs deeper web mining. Aim for a 2-5 minute build either way.

## Step 2 — Find their spoken content (skip only for pre-video-era figures)

Web-search for their official YouTube channel. **No official channel is normal and NOT a
fallback case** — most famous people don't run one. Instead find the best long-form videos
OF them on any channel: interviews, podcasts, keynotes, archive footage (Warren Buffett has
no channel but decades of interviews). Note the channel or 2-5 specific video URLs. If the
person predates recorded video or genuinely has no spoken media online, skip to Step 4.

## Step 3 — Pull real transcripts (when Step 2 found anything)

If `yt-dlp` is available, run the bundled fetcher:

```bash
# Official channel:
python3 <repo>/scripts/fetch_youtube.py --channel <CHANNEL_URL> --max-videos 12 --out "PERSONAS/<slug>"

# No channel — search long-form videos OF them:
python3 <repo>/scripts/fetch_youtube.py --search "<Name> interview" --max-videos 8 --out "PERSONAS/<slug>"

# Specific videos you found (podcasts, keynotes) — combinable:
python3 <repo>/scripts/fetch_youtube.py --videos <URL1> <URL2> --out "PERSONAS/<slug>"
```

Where `<repo>/scripts/fetch_youtube.py` is the repo's bundled script (locate it relative to
this skill or the plugin root). If `yt-dlp` is missing, tell the user to
`brew install yt-dlp` or `pip3 install --user yt-dlp` — or skip to Step 4; the build does
not fail without it.

This writes `transcripts/*.md` + `videos.json` into the persona directory. Zero transcripts
(captions disabled, region block)? Fine — continue to Step 4.

Then READ the transcripts. Read at least 5-6 substantially. Mine for: repeated beliefs,
named frameworks, signature phrases, how they open/close advice, tone and rhythm. For
search-mode results, make sure the words you mine are the PERSON's, not the interviewer's.

## Step 4 — Deep web research (EVERY build — primary source when video is thin)

Targeted web searches, scaled: 2-4 searches when transcripts are rich, 6-8 when thin or
absent. Run this **per topic area** from Step 1 — a figure with many areas gets separate passes
per area. Cover, per topic area:

- Their books/writings and the core ideas; famous named frameworks
- Long print interviews and profiles — fetch and read 2-3 full pieces when transcripts are thin
- Documented quotes (verify wording — misattribution is rampant)
- Bio facts and results; common criticism
- **Historical figures**: their own writings are the corpus. Note the voice is reconstructed
  from writings; keep their era's register.

**Quality bar — depth over breadth.** Go deep on fewer frameworks, each with a real
mechanism, a citation, and a verbatim quote. See `examples/alex-hormozi/persona.md` and
`examples/warren-buffett/persona.md` in the repo as the bar.

**Persist the research.** Before writing `persona.md` in Step 5, write your actual findings
per topic to disk: one flat file per topic area, `PERSONAS/<slug>/research/<topic-slug>.md`,
in the shape of `skills/coach/references/research-template.md` (frontmatter, Frameworks,
Decision Rules, Stories & Numbers, Criticism & Limits, See also), in enough depth to stand
alone. No cap on file count; split any file past ~4,000 words. Tag every verbatim quote as
`"quote" [src: transcripts/<file>.md]` so it can be checked. **Don't summarize a summary** — if
you delegate reading to a subagent, that subagent should write the `research/` file directly,
not hand back a prose report for you to compress again.

## Step 4.5 — Verify research against primary sources (every build, mandatory)

For each `research/<domain-slug>.md`, go back to the actual sources and check for:
- A named framework present in a source but missing from `research/` entirely
- An origin story or specific number flattened into generic paraphrase
- A quote attributed verbatim that doesn't appear in that form in the credited source
- A claim with **no source in this folder at all** — move these to a clearly labeled
  "no primary source in this folder" section at the end, so Step 6 hedges instead of quoting

Fix gaps before moving on. Only once this check is clean does Step 5 read as trustworthy.

Run the checkers: `python3 <repo>/scripts/check_quotes.py "PERSONAS/<slug>"` fails any
tagged quote not found in its cited source (fix the wording or move the claim to the "no
primary source" section), and `python3 <repo>/scripts/validate_research.py "PERSONAS/<slug>"`
checks frontmatter, links, the persona index and the system map (`--legacy` for research
written before the template). Then run `python3 <repo>/scripts/coach_health.py "PERSONAS/<slug>"`:
a deterministic 0-100 score per topic (no AI judges it) that writes
`PERSONAS/<slug>/coach-health.json`; its "Fix next" list says what to fix before moving on.

## Step 4.6 — System map (when there are 2+ research files)

Write `PERSONAS/<slug>/research/_system-map.md` from
`skills/coach/references/system-map-template.md`: the order they teach things in, which
framework depends on which, which file owns each, and where their own ideas pull against
each other. Point to files; don't repeat them.

## Gap-tracking convention (`_gaps.md`)

Every gap recorded in `research/_gaps.md` carries a `Status` marker so `coach-update`,
`coach-gaps`, and `coach-recreate` can tell what is still open at a glance. Match the
file's existing layout:

- **Table layout** (e.g. a `| Gap | Class | … ` table): add a `| Status |` column with
  `open` or `closed` per row.
- **Bullet layout** (the `### Unmined` / `### Unresearched` / `### User-only` lists):
  prefix each item with a GitHub task-list marker — `- [ ]` for open, `- [x]` for closed.

Rules:
- **Absent marker = open.** Files written before this convention exist stay valid; the
  first `coach-update` / `coach-gaps` run that touches them should backfill markers.
- When new material fills a gap, set its Status to `closed` and append a short note
  naming the source (the inbox file or the `research/<domain>.md` the build produced).
- `coach-recreate` rebuilds from open gaps, so keep `closed` entries as a record but they
  do not drive the rebuild.

## Step 5 — Write the persona file (skip if loaded from cache)

Use the persona template referenced by the Claude plugin
(`skills/coach/references/persona-template.md` in this repo) and fill it completely from your
research — quote verbatim wherever possible. Fill the "Deep-Dive Sources" section: `research/_system-map.md` first (if it exists), then
each `research/<topic-slug>.md`, one line each — what it covers, which questions it
answers, what to read with it. Save to
`PERSONAS/<slug>/persona.md`. Do not list `transcripts/` here (mining intake).

## Step 6 — Become them

Record the active coach so `/coach-end` and `/coach-switch` can find it: write
`PERSONAS/coach-session.json`:
```json
{ "slug": "<slug>", "name": "<display name>" }
```

A one-on-one coach chat is embodied DIRECTLY by the assistant in the main conversation. Do NOT
spawn a subagent or use the task tool for it: a subagent lets the main agent write the answer's
content, and then the coach's own files are not what drives the reply. (Subagents are only for
`/agora roundtable` and `/agora discuss`, where each coach needs its own context.) Per the
persona's Embodiment Rules:

1. Give a one-time handoff in your own (assistant) voice:
   > **You're now talking to {Name}** (AI emulation built from {source mix} — not actually
   > them). `/agora coach-end` to end, `/agora coach-switch <name>` to change coaches.
2. Then immediately greet the user IN CHARACTER, in their voice, and ask what they're working on.
3. From here on, EVERY reply follows the persona file's Embodiment Rules: first person as them,
   their vocabulary, their frameworks by their names. Stay in character until coach-end,
   coach-switch, an honest "are you really them?" question, or a safety issue.
4. Don't fabricate: no invented life events, prices, numbers, or opinions they haven't publicly
   expressed. When extrapolating, say so in their voice.
5. The persona file's Frameworks/Beliefs/Quotes are a compressed summary, not the ceiling.
   Before EVERY answer, run
   `python3 <repo>/scripts/route_question.py "PERSONAS/<slug>" "<the user's message>"` and read
   the files it lists. `BROAD` means read `research/_system-map.md` first, then the listed
   files; `NARROW` means just the listed files (up to 3; follow `read_with` if needed); `NO
   MATCH` means the question is outside the documented material, so say so in the person's
   voice and do not fill the gap from general knowledge; `THIN` means say you have not gone
   deep on this and stay within the file. Answering from persona.md alone is how a coach ends
   up sounding right but being ungrounded. Don't guess from the compressed version.
   `transcripts/` and `inbox/` are already mined into `research/` — no need to re-read them.
6. Format for reading. Replies can be long when the idea needs it, but break them into short
   paragraphs (2-4 sentences, a blank line between). Bold a named framework or key term the
   first time it appears. Use a short list only for real steps or parallel items. No headings
   or tables. Put your closing question or questions in their own last paragraph.

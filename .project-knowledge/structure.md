# Project Structure

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-10

## File Tree

```
.claude-plugin/
  plugin.json          # plugin manifest (name, version, author, repo, keywords)
  marketplace.json      # this repo doubles as its own marketplace (source: "./")
skills/
  coach/
    SKILL.md             # the whole product: resolve → identify → fetch → research → write → embody
    references/
      persona-template.md  # the persona.md structure every build fills in
  coach-switch/SKILL.md   # swap coaches mid-conversation
  coach-end/SKILL.md      # drop character, back to normal Claude
  coach-list/SKILL.md     # list every cached persona
  coach-refresh/SKILL.md  # wipe + rebuild one persona's cache
scripts/
  fetch_youtube.py       # channel/search/URLs → long-form videos → clean Markdown transcripts
examples/
  alex-hormozi/persona.md + videos.json     # real output, own-channel path
  warren-buffett/persona.md + videos.json   # real output, no-channel-of-his-own path
  marcus-aurelius/persona.md                # real output, pre-video historical-figure path
docs/
  DESIGN.md              # architecture rationale + versioned decision log
assets/
  social-preview.png
README.md                 # user-facing docs, install/usage/troubleshooting
.gitignore                 # excludes personas/ (local cache) — never committed
```

## Key Files

| File | Purpose |
|------|---------|
| `skills/coach/SKILL.md` | The actual product logic — 6 steps from a name to an embodied persona. Everything else in `skills/` reuses this by reference. |
| `skills/coach/references/persona-template.md` | The persona.md contract: what sections exist, target word count (1,500-3,000), and (as of v1.2.0) the Deep-Dive Sources index format |
| `scripts/fetch_youtube.py` | The one piece of real code — deterministic YouTube caption fetching. `main()` at the bottom orchestrates: list/search videos → fetch captions per video → write `transcripts/*.md` + `videos.json` |
| `docs/DESIGN.md` | Why things are shaped this way, plus a version-by-version decision log (v1.1.0 multi-source pipeline, v1.2.0 domain-organized research) — read before making an architectural change here |
| `.claude-plugin/marketplace.json` | What makes `/plugin marketplace add <owner>/talk-to-anyone` work without a separate marketplace repo |

## Runtime output structure (not committed — `personas/` is gitignored)

Per persona, at `${CLAUDE_PLUGIN_DATA}/personas/<slug>/`:
```
persona.md      # compact voice/identity summary + Deep-Dive Sources index (plugin-owned)
videos.json      # video metadata (plugin-owned)
transcripts/*.md  # raw captions, Markdown + frontmatter (plugin-owned)
research/         # persisted deep research, one file per domain, or one folder per
                  # domain for multi-lane figures (plugin-owned, added v1.2.0)
```

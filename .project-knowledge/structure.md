# Project Structure

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-29

## File Tree

```
.claude-plugin/
  plugin.json          # Claude Code plugin manifest (name, version, author, repo, keywords, based_on)
  marketplace.json      # this repo doubles as its own marketplace (source: "./")
skills/                  # Claude Code plugin — commands live here as skills
  coach/
    SKILL.md             # the whole product: resolve → identify → fetch → research → write → embody
    references/
      persona-template.md  # the persona.md structure every build fills in
  coach-switch/SKILL.md   # swap coaches mid-conversation
  coach-end/SKILL.md      # drop character, back to normal Claude
  coach-list/SKILL.md     # list every cached persona + saved presets
  coach-refresh/SKILL.md  # wipe + rebuild one persona's cache; runs coach-update logic after
  coach-refresh-all/SKILL.md  # rebuild all coaches or a named preset (v2.3.0)
  coach-update/SKILL.md       # explicit inbox sync for one coach (v2.2.0)
  coach-update-all/SKILL.md   # inbox sync for all coaches or a named preset (v2.3.0)
  coach-gaps/SKILL.md         # audit a coach's own sourcing thinness (v2.5.0)
  roundtable/SKILL.md         # start a multi-coach session; named presets (v2.1.0); agent-based (v2.4.0)
  roundtable-save/SKILL.md    # save/define named presets (v2.1.0)
  roundtable-add/SKILL.md     # add a coach mid-session
  roundtable-remove/SKILL.md  # remove a coach mid-session
  roundtable-end/SKILL.md     # end the roundtable
opencode-plugin/          # OpenCode port — full parity with the Claude skills, /agora* commands
  install.sh              # symlinks commands/agents/skills/plugin into ~/.config/opencode (idempotent)
  package.json            # declares @opencode-ai/plugin (for plugin.js)
  bun.lock
  commands/agora-*.md     # 15 slash commands (coach, coach-switch/end/list, coach-refresh[-all],
                          #   coach-update[-all], coach-gaps, roundtable, roundtable-save/add/remove/end, discuss)
  agents/
    agora-facilitator.md  # orchestrator: builds personas, runs warm-agent debates
    agora-coach.md        # hidden single-coach subagent (mode: subagent, hidden: true)
  skills/agora-coach/SKILL.md  # shared persona-building pipeline (same steps as skills/coach)
  plugin/plugin.js        # ESM plugin: agora_data_dir / agora_slugify / agora_session tools
  lib/data-dir.js         # portable data-dir resolver + slugify (the single source of truth for paths)
scripts/
  fetch_youtube.py       # channel/search/URLs → long-form videos → clean Markdown transcripts
examples/
  alex-hormozi/persona.md + videos.json     # real output, own-channel path
  warren-buffett/persona.md + videos.json   # real output, no-channel-of-his-own path
  marcus-aurelius/persona.md                # real output, pre-video historical-figure path
docs/
  DESIGN.md              # architecture rationale + versioned decision log (Claude side)
  opencode.md            # opencode port architecture, install, data-dir portability
assets/
  social-preview.png
README.md                 # user-facing docs, install/usage/troubleshooting
.gitignore                 # excludes personas/ (local cache) — never committed
```

## Key Files

| File | Purpose |
|------|---------|
| `skills/coach/SKILL.md` | The core persona pipeline — Steps 0-6 from a name to an embodied persona. Everything in `skills/coach-*` reuses this by reference. |
| `skills/roundtable/SKILL.md` | Multi-coach facilitator — reads the session JSON, handles 3 message types (general parallel agents, direct @name, /discuss sequential agents). Roundtable-add/remove/end update the JSON. |
| `skills/coach-update/SKILL.md` | Inbox processing — the only place that reads `inbox/` and writes into `research/`. Called explicitly by the user and by `coach-refresh` after a rebuild. |
| `skills/coach/references/persona-template.md` | The persona.md contract: what sections exist, target word count (1,500-3,000), and the Deep-Dive Sources index format |
| `scripts/fetch_youtube.py` | The one piece of real code on the Claude side — deterministic YouTube caption fetching. `main()` orchestrates: list/search videos → fetch captions per video → write `transcripts/*.md` + `videos.json` |
| `opencode-plugin/plugin/plugin.js` | The opencode-side runtime: three tools (`agora_data_dir`, `agora_slugify`, `agora_session`) that give the config-file commands the power they lack — resolving the portable data dir and persisting roundtable session/preset JSON. |
| `opencode-plugin/lib/data-dir.js` | **Single source of truth for where personas live** across both runtimes. Resolution order: `$AGORA_DATA_DIR` → `$CLAUDE_PLUGIN_DATA/agora-roundtable` (if exists) → `~/.config/opencode/agora` → `~/.claude/agora-roundtable` (if exists). |
| `opencode-plugin/install.sh` | Symlinks the bundle into `~/.config/opencode` so the repo stays the source of truth; links the personas dir to Claude's when present. |
| `docs/DESIGN.md` | Why things are shaped this way (Claude side), plus a version-by-version decision log — read before making an architectural change here |
| `docs/opencode.md` | Opencode port architecture: why commands/agents/skills are config files + a small JS plugin, install steps, data-dir portability |
| `.claude-plugin/marketplace.json` | What makes `/plugin marketplace add YahyaZekry/Agora-RoundTable` work without a separate marketplace repo |

## Runtime output structure (not committed — `personas/` is gitignored)

Per persona, in the resolved portable data dir (see `lib/data-dir.js`; on the Claude side
that's `${CLAUDE_PLUGIN_DATA}/agora-roundtable/personas/<slug>/`, on opencode
`~/.config/opencode/agora/personas/<slug>/` or `$AGORA_DATA_DIR/personas/<slug>/`):
```
persona.md              # compact voice/identity summary + Deep-Dive Sources index
videos.json              # video metadata
transcripts/*.md         # raw captions, Markdown + frontmatter — mined into research/,
                          # then archival, never a live reference target
research/<domain>.md     # the actual framework, one flat file per domain (v1.2.0,
                          # flattened v1.2.1) — everything else in this folder funnels
                          # into these files
inbox/                   # user drop zone — always created by /coach, even on cache hits.
                          # /coach-update reads here and writes into research/.
inbox/_sync-status.md    # manifest: file, date, coverage (complete/partial), target research/ file
                          # (not frontmatter — PDFs can't hold YAML frontmatter)
```

Also at DATA_DIR root (one per session):
```
roundtable-session.json  # active roundtable roster: { "coaches": [{slug, name}, ...] }
roundtable-presets.json  # named presets: { "y-table": ["thomas-harris", "joe-navarro"] }
```

If a persona folder is symlinked into an external vault (Yahya's setup: Obsidian, via a
`persona-sync` skill outside this repo), all of the above lives physically in the
vault — the plugin just reads/writes through the symlink transparently.

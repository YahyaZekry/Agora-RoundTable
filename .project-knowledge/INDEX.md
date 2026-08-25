# Agora RoundTable — Knowledge Index

> Last updated: 2026-08-24
> Status: Active
> Stack: Claude Code plugin (14 Markdown skills + 1 Python script), zero runtime services
> Current goal: v2.5.0 shipped (warm-agent debate + gap detection) — needs a real multi-round run against fully-built coaches to validate at scale

## What This Project Does

An independent Claude Code plugin (based on `coltonjosephdean-rgb/talk-to-anyone`, MIT
attributed) that turns any public figure into an AI coach persona. Two modes:

- **Single coach** — `/coach <name>` researches them across the web and YouTube, builds
  a persona file grounded in their real content, and Claude speaks as them for the rest
  of the conversation.
- **Roundtable** — `/roundtable <name1>, <name2>, ...` runs multiple built personas
  simultaneously. All coaches respond to each message in their own voice. Direct a
  question to one with `@name`, or use `/discuss <topic>` to have the coaches dialogue
  with each other, facilitated by Claude.

---

## Files in This Folder

| File | Contents | Load when... |
|------|----------|--------------|
| `stack.md` | Tech (Python + Markdown, no DB/build step), dev commands, the two `CLAUDE_PLUGIN_*` env vars | Touching `fetch_youtube.py`, adding a skill, checking how plugin paths resolve |
| `structure.md` | File tree, key files, the runtime (gitignored) per-persona output shape | Navigating the repo, understanding what a build actually produces on disk |
| `systems.md` | Persona cache, YouTube fetching, web research, AI embodiment — the actual cross-cutting concerns (no auth/DB/payments here) | Touching the research pipeline or the cache layout |
| `features.md` | All 13 slash commands + the build/embodiment/roundtable/inbox workflows, step by step | Understanding or changing how a persona gets built, or how roundtable works |
| `roadmap.md` | Current goal, active TODOs | Starting any task — know what's still pending |
| `history.md` | Architectural decisions (why `research/` exists, why transcripts are `.md`, why roundtable was added, why inbox is explicit) | Debugging or reconsidering a design choice |
| `sessions.md` | Session-by-session log | Reviewing what's been done |

> `schema.md`, `routes.md`, `hooks.md`, `components.md`, `integrations.md` don't exist
> — none apply to this project (no DB, no API routes, no UI components, no external
> systems reading/writing this project's data).

---

## Context Loading Guide

| Task | Load these files |
|------|-----------------|
| Changing `skills/coach/SKILL.md` or the research pipeline | `features.md` + `history.md` |
| Changing `skills/roundtable/SKILL.md` or roundtable behavior | `features.md` + `structure.md` |
| Changing `scripts/fetch_youtube.py` | `stack.md` + `structure.md` |
| Understanding the runtime persona-folder shape | `structure.md` |
| Picking up pending work | `roadmap.md` |
| General orientation (new session) | This file → then pick by task |
| Full audit | All files |

---

*Maintained with [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) · by [Yahya Zekry](https://github.com/YahyaZekry)*

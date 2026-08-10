# talk-to-anyone — Knowledge Index

> Last updated: 2026-08-10
> Status: Active
> Stack: Claude Code plugin (5 Markdown skills + 1 Python script), zero runtime services
> Current goal: push v1.2.0 (domain-organized research persistence) to `origin` and repoint the installed plugin from upstream to this fork so it's actually live

## What This Project Does

A fork of `coltonjosephdean-rgb/talk-to-anyone`, a Claude Code plugin that turns any
public figure into an AI coach persona. `/coach <name>` researches them across the web
and YouTube, builds a persona file grounded in their real content, and Claude speaks as
them for the rest of the conversation. This fork (`YahyaZekry/talk-to-anyone`) adds
domain-organized deep-research persistence on top of the original v1.1.0 pipeline.

---

## Files in This Folder

| File | Contents | Load when... |
|------|----------|--------------|
| `stack.md` | Tech (Python + Markdown, no DB/build step), dev commands, the two `CLAUDE_PLUGIN_*` env vars | Touching `fetch_youtube.py`, adding a skill, checking how plugin paths resolve |
| `structure.md` | File tree, key files, the runtime (gitignored) per-persona output shape | Navigating the repo, understanding what a build actually produces on disk |
| `systems.md` | Persona cache, YouTube fetching, web research, AI embodiment — the actual cross-cutting concerns (no auth/DB/payments here) | Touching the research pipeline or the cache layout |
| `features.md` | The 5 slash commands + the build/embodiment workflow, step by step | Understanding or changing how a persona gets built |
| `roadmap.md` | Current goal (push + repoint), active TODOs | Starting any task — know what's still pending |
| `history.md` | Architectural decisions from this session (why `research/` exists, why transcripts are `.md`) | Debugging or reconsidering a design choice |
| `sessions.md` | Session-by-session log | Reviewing what's been done |

> `schema.md`, `routes.md`, `hooks.md`, `components.md`, `integrations.md` don't exist
> — none apply to this project (no DB, no API routes, no UI components, no external
> systems reading/writing this project's data).

---

## Context Loading Guide

| Task | Load these files |
|------|-----------------|
| Changing `skills/coach/SKILL.md` or the research pipeline | `features.md` + `history.md` |
| Changing `scripts/fetch_youtube.py` | `stack.md` + `structure.md` |
| Understanding the runtime persona-folder shape | `structure.md` |
| Picking up pending work | `roadmap.md` |
| General orientation (new session) | This file → then pick by task |
| Full audit | All files |

---

*Maintained with [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) · by [Yahya Zekry](https://github.com/YahyaZekry)*

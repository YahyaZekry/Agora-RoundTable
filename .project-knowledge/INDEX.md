# Agora RoundTable — Knowledge Index

> Last updated: 2026-10-18
> Status: Active
> Stack: Three runtimes — Claude Code + OpenCode + Codex plugins, shared persona format & agent-neutral data dir (`~/.agora`, override `$AGORA_DATA_DIR`), zero runtime services
> Current goal: Validate the warm-agent debate at scale across all three runtimes, then rebuild the novel-coaching persona stubs that gate that test

## What This Project Does

A Claude Code, OpenCode, and Codex plugin that turns any
public figure into an AI coach persona. Ships for **three hosts** with identical capability
and a shared persona format: **Claude Code** (`/coach`, `/roundtable`, `/discuss`) and
**OpenCode** (`/agora coach`, `/agora roundtable`, `/agora discuss`), and **Codex**
(`coach`, `roundtable`, and related skills). Two modes:

- **Single coach** — `/coach <name>` (or `/agora coach`) researches them across the web
  and YouTube, builds a persona file grounded in their real content, and the host model
  speaks as them for the rest of the conversation.
- **Roundtable** — `/roundtable <name1>, <name2>, ...` runs multiple built personas
  simultaneously. All coaches respond to each message in their own voice. Direct a
  question to one with `@name`, or use `/discuss <topic>` to have the coaches dialogue
  with each other, facilitated by the host model.

---

## Files in This Folder

| File | Contents | Load when... |
|------|----------|--------------|
| `stack.md` | Three-runtime tech (Claude + OpenCode + Codex), dev/install commands, and the agent-neutral data dir (`~/.agora`, override `$AGORA_DATA_DIR`) | Touching `fetch_youtube.py`, a runtime port, adding a skill, checking how plugin paths resolve |
| `structure.md` | File tree (all runtimes), key files, the runtime (gitignored) per-persona output shape | Navigating the repo, understanding what a build actually produces on disk |
| `systems.md` | Portable persona cache + data-dir resolver, OpenCode JS plugin, Codex plugin packaging, YouTube fetching, web research, AI embodiment | Touching the research pipeline, the cache layout, or a runtime integration |
| `features.md` | Three-runtime coaching and roundtable workflows, all 15 skills, and the build/embodiment/inbox paths | Understanding or changing how a persona gets built, or how roundtable works |
| `roadmap.md` | Current goal, active TODOs | Starting any task — know what's still pending |
| `history.md` | Architectural decisions (why `research/` exists, why transcripts are `.md`, why roundtable was added, why inbox is explicit, why the opencode port is a hybrid) | Debugging or reconsidering a design choice |
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
| Changing the opencode port (`opencode-plugin/`) | `features.md` + `structure.md` + `systems.md` (data-dir resolver) |
| Changing Codex packaging (`.codex-plugin/` or `.agents/plugins/`) | `stack.md` + `structure.md` + `systems.md` |
| Changing `scripts/fetch_youtube.py` | `stack.md` + `structure.md` |
| Understanding the runtime persona-folder shape | `structure.md` |
| Picking up pending work | `roadmap.md` |
| General orientation (new session) | This file → then pick by task |
| Full audit | All files |

---

*Maintained with [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) · by [Yahya Zekry](https://github.com/YahyaZekry)*

---
description: Start a multi-coach session with two or more built personas.
agent: agora-facilitator
subtask: true
---
Start an Agora roundtable with the coaches in $ARGUMENTS (comma-separated names, or a preset name). Resolve the shared data dir. If $ARGUMENTS is a single token matching roundtable-presets.json, load those coaches; otherwise parse the comma-separated names. Slugify each, verify each PERSONAS/<slug>/persona.md exists (list any unbuilt and tell the user to /agora coach each one first — do NOT auto-build; require at least two ready). Write roundtable-session.json with the active coaches. Print a one-time handoff explaining: ask everyone (just type — all respond in turn), direct to one (@name), facilitated discussion (/agora discuss <topic>), and manage (/agora roundtable-add / remove / end). Then stay in roundtable facilitation mode: on every user message spawn each coach as its own subagent and synthesize — never simulate a coach's voice yourself.

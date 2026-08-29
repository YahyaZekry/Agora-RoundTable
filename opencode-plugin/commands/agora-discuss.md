---
description: Run a real multi-round debate between the active roundtable coaches.
agent: agora-facilitator
subtask: true
---
Facilitate a multi-round warm-agent debate on: $ARGUMENTS. Read roundtable-session.json for the active coaches. This uses WARM agents: each coach is a dedicated subagent spawned once and RESUMED across rounds so it keeps its own context and can say "you've moved me."

Round 1 (parallel cold spawn): spawn each coach subagent simultaneously, each reading its own persona.md + most relevant research/ file. Prompt: state a clear position on the topic, no hedging, respond IN CHARACTER, 2-4 paragraphs, ending with a META block (movedBy/none, newArgument/yes, wantsToPress/@name). Show responses labeled, strip META.

Rounds 2..N (parallel warm): resume each subagent with the OTHERS' last statements. Prompt them to respond directly, say where the others are wrong and where (if anywhere) they've been moved, address by name, and re-report the META block.

Stop conditions after each round: CONVERGED (positions merged / synthesis everyone accepts), CRYSTALLIZED (a full round where every coach reported movedBy:none AND newArgument:no — still disagree, report as a fully-developed choice, a success not a failure), or CAPPED at 5 rounds (say it plainly, never present as finished). Do NOT keep pushing for agreement once positions crystallize.

Synthesis: in facilitator voice, 3-5 lines on what converged, what stayed contested, and which terminal state was reached.

Gap check: resume each subagent once more, OUT of character, asking where they were thin (claims with no source, what material would have helped them argue better, what kind of source would fix it). Then route gaps per the coach-gaps classification and append to each coach's research/_gaps.md. Surface only what's actionable to the user.

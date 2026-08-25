# Roadmap

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-23

## Current Goal

v2.5.0 shipped: `/discuss` runs multi-round warm-agent debate until positions stop
moving, then reports where each coach's own sourcing was thin and routes the gaps.
Mechanism proven on a 2-coach test. Needs a real run against fully-built coaches —
the stub personas are the blocker.

---

## Known Bugs

*(none identified)*

---

## Active TODOs

- [ ] **Rebuild novel coaching personas with full pipeline** — Thomas Harris, Joe Navarro,
      Gillian Flynn, Dennis Lehane all only have `persona.md` stubs (no `research/`,
      most have no `transcripts/`). Run `/coach-refresh` for each. Blocks a real test of
      v2.5.0's debate and gap detection — a coach with no `research/` can only report
      "everything is thin." *(added: 2026-08-23)*
- [ ] **Validate v2.5.0 at scale** — the proof run was 2 coaches, 2 rounds. Untested:
      3+ coaches in a round, the `wantsToPress` 1v1 narrowing, hitting the 5-round cap,
      and whether `_gaps.md` entries actually get closed correctly by a later
      `/coach-refresh`. *(added: 2026-08-24)*
- [ ] **Old `talk-to-anyone` plugin removed but skills may still be cached** — user
      removed it; `/coach-refresh-all` was not resolving. Verify after a Claude Code
      restart that all 14 commands resolve under `agora-roundtable`.
      *(added: 2026-08-24)*
- [ ] Run the Step 4.5 pass against the Goggins persona's `inbox/` and coverage the
      same way Hormozi was checked — v1.2.3 fixed its `research/` for accuracy, but
      that was before coverage and unsourced-claim checks existed *(added: 2026-08-19)*

### Open on the Hormozi persona itself (vault-side, not the repo)

- [ ] `Your_ACQ_100MScalingRoadmap-Stage0_.pdf` — only pages 1-3 of ~10 stages read,
      now correctly logged partial *(added: 2026-08-19)*
- [ ] 5 quotes attributed to Modern Wisdom #830 and "The Game" can't be verified —
      no copy of either in the folder; marked ⚠️ until the raw sources land in `inbox/`
      *(added: 2026-08-19)*
- [ ] The dossier's Gym Launch ad story identifies the customer as "the person who
      would later become U.S. president" — reproduced faithfully but never checked
      against the original video and not independently plausible *(added: 2026-08-19)*

---

## Planned Features

*(none stated beyond what's been built — no speculative roadmap items added)*

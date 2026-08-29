# Roadmap

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-29

## Current Goal

v2.5.0 (warm-agent debate + use-driven gap detection) shipped on the Claude side and is
mirrored in the new **opencode port** (`opencode-plugin/`, full `/agora*` command parity,
still uncommitted). Two things remain: (1) validate the warm-agent debate at scale against
fully-built coaches, and (2) commit + smoke-test the opencode port.

---

## Known Bugs

*(none identified)*

---

## Active TODOs

- [ ] **Commit and smoke-test the opencode port** — `opencode-plugin/` and `docs/opencode.md`
      are still untracked/uncommitted. Verify install (`bash opencode-plugin/install.sh`),
      that all 15 `/agora*` commands resolve after restart, and that personas share with the
      Claude dir when present. *(added: 2026-08-29)*
- [ ] **Rebuild novel coaching personas with full pipeline** — Thomas Harris, Joe Navarro,
      Gillian Flynn, Dennis Lehane all only have `persona.md` stubs (no `research/`,
      most have no `transcripts/`). Run `/coach-refresh` for each. Blocks a real test of
      v2.5.0's debate and gap detection — a coach with no `research/` can only report
      "everything is thin." *(added: 2026-08-23)*
- [ ] **Validate v2.5.0 at scale** — the proof run was 2 coaches, 2 rounds. Untested:
       3+ coaches in a round, the `wantsToPress` 1v1 narrowing, hitting the 5-round cap,
       and whether `_gaps.md` entries actually get closed correctly by a later
       `/coach-refresh`. Also untested on the opencode port's `agents/agora-*` subagents.
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

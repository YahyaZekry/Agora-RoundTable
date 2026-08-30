# Roadmap

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-30

## Current Goal

v2.5.1 shipped on both runtimes: `/coach-refresh` no longer deletes before it rebuilds,
and `/coach-update` now closes all three kinds of gap without rebuilding anything. The
opencode port is committed and at parity. Remaining: run an end-to-end test of the gap
flow against a real coach, and validate the warm-agent debate at scale.

---

## Known Bugs

*(none identified)*

---

## Active TODOs

- [ ] **Smoke-test the opencode port** — committed as of 2026-08-29. Still unverified:
      install (`bash opencode-plugin/install.sh`), that all 15 `/agora*` commands resolve
      after restart, and that personas share with the Claude dir when present.
      *(added: 2026-08-29)*
- [ ] **End-to-end test the v2.5.1 gap flow** — `/coach-gaps` on a real coach to record
      gaps, then `/coach-update` to close them, checking each kind routes correctly and
      that `_gaps.md` is deleted when everything closes and gets a status header when it
      does not. Never actually run start-to-finish. *(added: 2026-08-30)*
- [ ] **Verify the refresh backup path actually restores** — force a build failure and
      confirm `.refresh-backup/` is put back and nothing is lost. The safety net is
      written but untested. *(added: 2026-08-30)*
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

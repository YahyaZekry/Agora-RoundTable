# Roadmap

> Part of agora-roundtable/.project-knowledge/ | Last updated: 2026-08-30 (2)

## Current Goal

v2.5.1 shipped on both runtimes: `/coach-refresh` no longer deletes before it rebuilds,
and `/coach-update` now closes all three kinds of gap without rebuilding anything. The
opencode port is committed and at parity. The gap flow has now been run end to end on Plato in
both runtimes and the output spot-verified against primary text. Remaining: validate the
warm-agent debate at scale, and get the user's two outstanding persona decisions.

---

## Known Bugs

*(none identified)*

---

## Active TODOs

- [ ] **Smoke-test the opencode port** — committed as of 2026-08-29. Still unverified:
      install (`bash opencode-plugin/install.sh`), that all 15 `/agora*` commands resolve
      after restart, and that personas share with the Claude dir when present.
      *(added: 2026-08-29)*
- [x] ~~**End-to-end test the v2.5.1 gap flow**~~ — **DONE 2026-08-30.** Ran on Plato.
      Claude side closed 4 unmined gaps (one turned out already closed — stale entry);
      the opencode side then closed all 9 unresearched plus the blocked 518b–d item.
      Spot-verified *Republic* 518b–d against the Internet Classics Archive: all three
      phrases word-for-word. The run also correctly caught that the old Symposium wording
      was Jowett's *Introduction* rather than dialogue text, which is exactly the
      discrimination the gap existed to enforce. Purely additive, nothing clobbered.
- [ ] **Two Plato decisions are waiting on the user** — which translation the persona
      quotes in (currently all Jowett 1892), and how to treat the disputed Seventh Letter
      that carries the whole Syracuse biography. Both sit in `plato/inbox/` as questions.
      *(added: 2026-08-30)*
- [ ] **Re-check whether the Phaedo-immortality gap is still blocked** — it was left open
      because extracting it would propagate unverified text, but the research pass has
      since run. Likely closeable now. *(added: 2026-08-30)*
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

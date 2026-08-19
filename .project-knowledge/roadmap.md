# Roadmap

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-19

## Current Goal

None active — v1.2.4 is live on `origin/main` (`f378d98`) and the installed plugin
already points at this fork. The plugin is self-sufficient end to end: build, deep
research, inbox extraction, verification, embodiment. First upstream PR is open:
coltonjosephdean-rgb/talk-to-anyone#1.

---

## Known Bugs

*(none identified)*

---

## Active TODOs

- [ ] Reinstall the plugin from the fork to pick up v1.2.4 — `/plugin install` alone
      doesn't pull new commits; needs a full marketplace remove+re-add, which wipes the
      plugin data dir and breaks persona symlinks (run `persona-sync` after)
      *(added: 2026-08-19)*
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

# Roadmap

> Part of talk-to-anyone/.project-knowledge/ | Last updated: 2026-08-19

## Current Goal

v2.0.0 built, not yet pushed. Roundtable feature complete. Repo detached from fork
(now `YahyaZekry/talk-to-anyone`, independent, MIT attributed). Blocked on name
decision — Yahya is choosing between keeping `talk-to-anyone` or renaming to something
like `summon` or `council`. Name decision gates the push.

---

## Known Bugs

*(none identified)*

---

## Active TODOs

- [ ] **Decide the plugin name** — options on the table: `summon`, `council`, keep
      `talk-to-anyone`. Name change requires updating: both JSON manifests, fallback
      DATA_DIR path in all skill files, command namespace prefix, GitHub repo rename,
      README install command. *(added: 2026-08-22)*
- [ ] **Push v2.0.0 to `origin/main`** — after name decision *(added: 2026-08-22)*
- [ ] **Reinstall the plugin** — after push: full marketplace remove+re-add (not just
      `/plugin install`), then `persona-sync` to recreate the symlinks the reinstall
      wipes *(added: 2026-08-22)*
- [ ] **Build the novel coaching personas** — Thomas Harris, Gillian Flynn, Dennis
      Lehane, Joe Navarro. These are the first real roundtable use case. Build with
      `/coach`, run `persona-sync`, then test `/roundtable thomas harris, gillian flynn`
      *(added: 2026-08-22)*
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

# Change Log

Newest entries last. Each milestone gets a dated entry that matches the roadmap status and the GitHub issue comments.

## 2026-10-31

- P0 workflow bootstrap: adapted the UBC-FRESH seed to fresh-cbm, added the
  agent contract, roadmap/issue map, notes, changelog, workflow validator,
  dashboard, pre-commit parity, Sphinx documentation, and GitHub Pages deploy
  workflow. Parent issue: #1. Dashboard and docs build are the acceptance gates.

- P0 close-out: PR #2 squash-merged as `732e874`. CI and the docs deploy are
  green. The published site is https://ubc-fresh.github.io/fresh-cbm/. Parent
  issue #1 closed. Next phase is planned in `ROADMAP.md`.

- P1.1 context and architecture docs: added `guides/context`, `guides/applications`,
  and `reference/architecture`; expanded the README with target applications and
  non-goals; updated the docs index and `llms.txt`. Dashboard: GREEN.

- P1 close-out: PR #7 squash-merged as `5d2137b`. Context, applications, and
  architecture pages are live; dashboard and docs are green. Parent issue #5 and
  task #6 closed. Next phase is planned in `ROADMAP.md`.

- P2.1 package CLI and integrity: moved the builder, validator, and release logic
  behind the `fresh-cbm-build`, `fresh-cbm-validate`, and `fresh-cbm-package`
  console entry points; kept the scripts as compatibility wrappers. Added
  `StateCache.validate` for index/state/file/shape checks and
  `StateCache.verify_checksums` for `SHA256SUMS`. Added command and integrity
  documentation and tests for malformed caches and checksums. Dashboard: GREEN.

- P2 close-out: PR #11 squash-merged as `1a2b9d5`. Console entry points and
  cache integrity checks are live; dashboard, docs, and CI are green. Parent
  issue #9 and task #10 closed. Next phase is planned in `ROADMAP.md`.

- P3.1 chain-family contract: added `fresh_cbm.family.ChainFamily`, wrote it into
  new manifests, exposed it through `StateCache.chain_family`, and made the client
  reject family/offset/empty-policy mismatches. Legacy manifests without a family
  still load. Builder options include `--treatment`, `--events`, and `--no-empty`;
  more than one event is rejected. Dashboard: GREEN.

- P3.2 reusable effect adapter: added `fresh_cbm.effects.build_block_effects` and
  `BlockEffects`. It maps cached state rows through block fragments and area
  weights to target cells without importing WS4, supports multi-fragment blocks,
  and validates cells, tracks, ages, and chain offsets. Tests cover aggregation,
  totals, and invalid inputs. Dashboard: GREEN.

- P3.3 second package cache: built and released TSA08, 3,761 states × 51 chains,
  2.03 GB, in 7,551.7 s. Validation of 102 sampled rows had max absolute error
  zero. Release:
  https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa08. Also added
  `--ws4-path` to the builder/validator so the installed commands fail clearly
  when WS4 is absent. Evidence: `notes/reports/p3-3-tsa08-cache.md`.

- P3.4 benchmarks: added `fresh-cbm-bench` and measured both published caches.
  TSA41: 2.85 GB, 5,273 states, 0.018 s load, 0.85 ms median lookup, 2.33 s
  projection over 148,828 blocks. TSA08: 2.03 GB, 3,761 states, 0.032 s load,
  1.18 ms lookup, 4.96 s projection over 371,565 blocks. Evidence:
  `notes/reports/p3-4-benchmarks.md`.

- P3 close-out: chain-family contract, reusable effect projection, TSA08 cache,
  and cache/projection benchmarks are merged. Parent issue #13 closed; P4 is
  planned in `ROADMAP.md`. Dashboard and docs green.

- P4.1/P4.2 verification and release hardening: added `fresh-cbm-verify` for
  offline shape/checksum/release checks; verified both public caches (TSA41
  2.85 GB, TSA08 2.03 GB, checksums and release metadata consistent); added a CI
  wheel/sdist install smoke job; and expanded the release checklist. Dashboard:
  GREEN.

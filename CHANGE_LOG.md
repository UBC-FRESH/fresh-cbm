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

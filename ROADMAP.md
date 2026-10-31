# fresh-cbm Roadmap

This roadmap is the plan of record and the issue tracker map for fresh-cbm. Keep it in step with the GitHub issues, `CHANGE_LOG.md`, and `notes/`. `scripts/check_workflow.py` parses the phase headers, status lines, and checkboxes below, so keep their format.

Every phase starts as `planned` with `Parent issue: TBD`. Activate a phase only after its parent issue exists and the maintainer approves it. P0 is active under issue #1.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap | #1 | `feature/p0-workflow-bootstrap` | complete |
| P1 Scope and design | #5 | `feature/p1-docs-context` | complete |
| P2 Contracts and prototype | #9 | `feature/p2-package-cli` | complete |
| P3 Build | TBD | `feature/p3-build` | planned |
| P4 Verify | TBD | `feature/p4-verify` | planned |
| P5 Release and deploy | TBD | `feature/p5-release` | planned |
| P6 Operate and maintain | TBD | `feature/p6-operate` | planned |

## Lifecycle Map

| Stage | Phases | Exit criteria |
| --- | --- | --- |
| Scope and design | P0, P1 | Goal, scope, and out-of-scope items recorded; decisions in ADRs, each accepted or deferred |
| Build | P2, P3 | Each task committed with its task ID; each commit leaves the dashboard green; docs updated in the same change set |
| Verify | P4 | The dashboard and CI pass on the head commit; each acceptance criterion has evidence in the close-out report |
| Release and deploy | P5 | Tag, release notes, and Pages live; a clean checkout verifies them; each release action approved on its own |
| Operate and maintain | P6 | Review cadence held; incoming ideas triaged; retirement decided and recorded as an ADR |
| Retire | P6 (procedure) | Archive notice, final changelog entry, and issues closed |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside the task's issue body. Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and its parent issue closes.

## Phase 0: Bootstrap

Parent issue: #1
Branch: `feature/p0-workflow-bootstrap`
Status: complete

Goal: adapt the UBC-FRESH workflow to fresh-cbm, add the Sphinx site, and make the first pull request reviewable.

- [x] P0.1 Adapt `AGENTS.md`, `README.md`, `ROADMAP.md`, `CHANGE_LOG.md`, and `notes/`
- [x] P0.2 Add Sphinx docs and the GitHub Pages deploy workflow
- [x] P0.3 Add the workflow validator, dashboard, CI, and pre-commit parity
- [x] P0.4 Verify the docs build and the published Pages site

Acceptance criteria:

- `python scripts/check_workflow.py` passes
- `python scripts/dashboard.py` is green
- CI is green on Python 3.11 and 3.12
- the docs site is published from `main` on GitHub Pages

## Phase 1: Scope and design

Parent issue: #5
Branch: `feature/p1-docs-context`
Status: complete

Goal: make the package understandable to a new reader: context, target applications, architecture, and boundaries.

- [x] P1.1 Add a context and target-applications guide
- [x] P1.2 Add an architecture and data-flow reference
- [x] P1.3 Add a worked application example, limitations, and FAQ

Acceptance criteria:

- a new reader can explain the cache in five minutes
- the docs name intended consumers and non-goals
- the docs connect the cache to WS4's state-cache consumer
- `sphinx-build -W` and the workflow validator pass

## Phase 2: Contracts and prototype

Parent issue: #9
Branch: `feature/p2-package-cli`
Status: complete

Goal: make the package installable and fail-safe at the cache boundary.

- [x] P2.1 Add console entry points and cache integrity validation
- [x] P2.2 Document the entry points and integrity contract
- [x] P2.3 Verify installed-package behavior in CI

Acceptance criteria:

- `pip install -e .` exposes all three commands
- malformed or truncated caches fail before lookup
- checksum verification is available and tested
- dashboard, docs, and CI pass

## Phase 3: Build

Parent issue: TBD
Branch: `feature/p3-build`
Status: planned

Goal: implement the agreed scope, one task at a time, on the phase branch.

- [ ] P3.1 Implement the first build task

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 4: Verify

Parent issue: TBD
Branch: `feature/p4-verify`
Status: planned

Goal: show that the build meets its acceptance criteria, and record the evidence in the changelog.

- [ ] P4.1 Run the acceptance checks and record the evidence

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 5: Release and deploy

Parent issue: TBD
Branch: `feature/p5-release`
Status: planned

Goal: tag a release, publish the docs, and verify the published artifacts from a clean checkout.

- [ ] P5.1 Write the release notes and the known-gaps list
- [ ] P5.2 Tag, publish, and verify from a clean checkout (maintainer approval required)

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 6: Operate and maintain

Parent issue: TBD
Branch: `feature/p6-operate`
Status: planned

Goal: keep the project current: triage incoming ideas, review on a cadence, and close out cleanly.

- [ ] P6.1 Set a review cadence and record the first review

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Detailed Next Steps Notes

1. Create the GitHub repository and the Phase 0 parent issue. This needs maintainer approval.
2. Activate Phase 0 by setting its parent issue number and its status to `active`, here and in the tracker map.

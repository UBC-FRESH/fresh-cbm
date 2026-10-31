# P6 close-out: operation and maintenance

Phase identifier: P6
Status: complete
Parent issue: #33
Task issue: #34

## Outcome

- maintenance and compatibility policy published
- review cadence: monthly health, quarterly dependency/compatibility, annual
  rebuild planning, event-driven cache triggers
- first review recorded at `notes/reviews/2026-10-31.md`
- next review: 2026-11-30

## Evidence

- docs: https://ubc-fresh.github.io/fresh-cbm/reference/maintenance.html
- dashboard: GREEN
- validator: 0 errors
- docs `-W`: GREEN
- tests: 173 passed
- package release: v0.2.0
- cache releases: v0.1.0-tsa41, v0.1.0-tsa08

## Current known gaps

- TSA41 legacy manifest predates `chain_family`.
- Multi-event chains and fertilization variants are not cached.
- PyPI is not enabled.
- Exact whole-schedule replay is outside the benchmark.

## Next

P6 is the final lifecycle phase. New cache families or external publication
decisions start a new approved phase.

# P2 close-out: package CLI and integrity hardening

Phase identifier: P2
Status: complete
Parent issue: #9
Task issue: #10
Pull request: #11
Merge commit: `1a2b9d5`

## Outcome

`fresh-cbm` is installable as a package with stable commands:

- `fresh-cbm-build`
- `fresh-cbm-validate`
- `fresh-cbm-package`

The builder, validator, and release logic now live in `fresh_cbm` modules; the
scripts are compatibility wrappers.

`StateCache.load` validates the index, state count, file set, and array shapes.
`StateCache.verify_checksums` verifies `SHA256SUMS`. The commands and integrity
contract are documented.

## Evidence

- `python scripts/dashboard.py`: **GREEN**
- `python scripts/check_workflow.py`: **0 errors, 0 warnings**
- `sphinx-build -b html docs _build/html -W`: **GREEN**
- tests: **151 passed**, **91.49% branch coverage**
- CI run: https://github.com/UBC-FRESH/fresh-cbm/actions/runs/41179255656
- commands page: https://ubc-fresh.github.io/fresh-cbm/api/commands.html

## Next

P3 is planned for cache-coverage and consumer-contract work.

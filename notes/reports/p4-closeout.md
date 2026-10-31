# P4 close-out: verification and release hardening

Phase identifier: P4
Status: complete
Parent issue: #25
Task issue: #26
Pull request: #27
Merge commit: `f00e80f`

## Outcome

- `fresh-cbm-verify` performs offline manifest/index/array, checksum, and
  release-metadata verification.
- both published caches verified:
  - TSA41: 5,273 states, 2.85 GB
  - TSA08: 3,761 states, 2.03 GB
- CI includes a wheel and sdist install smoke job for all console commands.
- release guide includes verification.

## Evidence

- dashboard: GREEN
- validator: 0 errors
- docs `-W`: GREEN
- tests: 173 passed
- coverage: 90.36%
- CI: https://github.com/UBC-FRESH/fresh-cbm/actions/runs/41223880191
- verifier docs: https://ubc-fresh.github.io/fresh-cbm/api/verify.html

## Next

P5 is planned for release/deploy, including package tagging and PyPI decision.

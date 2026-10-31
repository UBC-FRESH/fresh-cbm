# P3 close-out: cache coverage and consumer projection

Phase identifier: P3
Status: complete
Parent issue: #13

## Outcome

- P3.1: explicit `ChainFamily` contract, manifest metadata, builder options, and
  client validation. PR #15.
- P3.2: reusable `fresh_cbm.effects.build_block_effects` projection. PR #18.
- P3.3: second package cache, TSA08, 3,761 states × 51 chains, 2.03 GB, max
  validation error 0. PR #21.
- P3.4: `fresh-cbm-bench`; TSA41 projection 2.33 s over 148,828 blocks, TSA08
  4.96 s over 371,565 blocks. PR #23.

## Evidence

- dashboard: GREEN
- validator: 0 errors
- docs `-W`: GREEN
- tests: 170 passed, 92.07% branch coverage
- docs: https://ubc-fresh.github.io/fresh-cbm/
- releases: `v0.1.0-tsa41`, `v0.1.0-tsa08`

## Next

P4 is planned for verification and release hardening.

# P4: verification and release hardening

Phase identifier: P4
Status: complete
Parent issue: #25
Task issue: #26

## Added

- `fresh-cbm-verify`: offline cache shape, checksum, and release-metadata
  verification without WS4.
- tests for valid, tampered, missing-checksum, and release-mismatch cases.
- CI wheel/sdist install smoke job.
- release guide now includes `fresh-cbm-verify`.

## Published cache verification

| Cache | States | Bytes | Checksums | Release metadata |
| --- | ---: | ---: | --- | --- |
| TSA41 | 5,273 | 2,852,792,991 | pass | pass |
| TSA08 | 3,761 | 2,034,777,166 | pass | pass |

## Evidence

- dashboard: GREEN
- validator: 0 errors
- docs `-W`: GREEN
- tests: 173 passed
- coverage: 90.36%
- CI wheel and sdist smoke tests: configured
- releases:
  - https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa41
  - https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa08

## Boundary

Verification checks cache integrity and release metadata. It does not rerun
libcbm; the exact builder/validator paths remain the authority for scientific
content.

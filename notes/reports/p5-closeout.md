# P5 close-out: package release and deployment

Phase identifier: P5
Status: complete
Parent issue: #29
Task issue: #30
Release PR: #31
Release: https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.2.0
Tag target: `d45799afb9f3c16ba57810e92efff98beb14abc7`

## Release

- version: `0.2.0`
- wheel: `fresh_cbm-0.2.0-py3-none-any.whl`
- sdist: `fresh_cbm-0.2.0.tar.gz`
- artifact checksums: uploaded as `SHA256SUMS`
- wheel and sdist installed in clean venvs; every console command smoke-tested
- CI wheel/sdist job green

## PyPI

PyPI publication was **not performed**. The GitHub release is the distribution
channel for this phase. Publishing to PyPI still needs a separate maintainer
decision and credentials.

## Evidence

- release: https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.2.0
- docs: https://ubc-fresh.github.io/fresh-cbm/
- dashboard: GREEN
- validator: 0 errors
- docs `-W`: GREEN
- tests: 173 passed

# fresh-cbm

Exact cached libcbm stand-state tables and lookup client for WS4/FEMIC carbon
analyses.

`fresh-cbm` stores the deterministic per-hectare carbon accounts produced by
libcbm for a declared package and treatment family. Consumers can look up a
stand state instead of rebuilding a CBM model for every analysis.

## Documentation

Published Sphinx site:

https://ubc-fresh.github.io/fresh-cbm/

Start with the cache format, building, and validation guides.

## Status

Phase P0 (workflow bootstrap and documentation) is complete. `ROADMAP.md` is the
plan of record; P1 is planned.

## Quick start

```bash
python -m pip install -e ".[test]"
fresh-cbm-build --help
fresh-cbm-validate --help
fresh-cbm-package --help
fresh-cbm-bench --help
fresh-cbm-verify --help
python -m pytest
python scripts/dashboard.py
sphinx-build -b html docs _build/html -W
```

The builder and validator require WS4 (`ws4[carbon]`). Pass `--ws4-path` or put
the WS4 source root on `PYTHONPATH`; the client and tests do not.

## Available cache

`v0.1.0-tsa41` is the first published table:

- 5,273 TSA41 track/age states
- declared family: untreated + one `CC` event at offsets `0..49`
- 50 years, 26 carbon accounts, float64
- 2.85 GB
- 55 release assets
- validation: 102 sampled state/offset rows, max absolute error 0

Release:
https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa41

`v0.1.0-tsa08` is the second package cache:

- 3,761 TSA08 track/age states
- untreated + `CC@0..49`
- 50 years, 26 accounts, float64
- 2.03 GB
- build 2h05; validation 102 rows, max absolute error 0

Release:
https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa08

## Benchmarks

`fresh-cbm-bench` measures load, lookup, projection, and storage. On the published
TSA41 cache, projection over 148,828 blocks took **2.33 s**; TSA08 over 371,565
blocks took **4.96 s**. See `docs/guides/benchmarks.rst`.

## How this project works

This project follows the UBC-FRESH dev workflow. Work is planned as phases,
tasks, and subtasks in `ROADMAP.md`, mirrored in GitHub issues, and recorded in
`CHANGE_LOG.md`. The agent contract is `AGENTS.md`. Read `AGENTS.md` and
`ROADMAP.md` before changing anything.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating contract for coding agents |
| `ROADMAP.md` | Plan of record and issue tracker map |
| `CHANGE_LOG.md` | Dated narrative of changes |
| `docs/` | Sphinx site, published to GitHub Pages |
| `notes/` | Decisions and focused plans |
| `fresh_cbm/` | Python client, manifest schema, family contract, and effect projection |
| `scripts/` | Builder, validator, workflow validator, and dashboard |
| `tests/` | pytest suite |

## License

Apache-2.0. See `LICENSE`.

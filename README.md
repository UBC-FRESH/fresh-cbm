# fresh-cbm

Exact, reusable **libcbm stand-state cache** for WS4/FEMIC carbon analyses.

`fresh-cbm` does not replace libcbm. It stores the exact per-hectare carbon
accounts produced by libcbm for a declared state family, so repeated WS4 carbon
searches can look up a state instead of rebuilding a CBM model.

## What is cached

A state is:

```text
(package fingerprint, track_id, age, treatment chain, config hash)
    -> years x carbon accounts
```

The cache is exact for the source package, CBM defaults, libcbm version, HWP
configuration, and horizon in its manifest. A mismatch must fall back to libcbm.

The cache does **not** contain:

- block areas or fragment mappings
- spatial topology or adjacency
- planning targets
- route or patch rules

Those remain dataset-specific. A block effect is an area-weighted sum of state
rows.

## Layout

```text
manifest.json
index.parquet          # state_id, track_id, track_name, age, chain_offset
values/offset_XX.npy   # [states, years + 1, accounts]
values/empty.npy       # untreated chain
blocks.parquet         # optional dataset block -> state mapping
```

`manifest.json` records the package fingerprint, libcbm version, CBM defaults
hash, years, account names, dtype, offsets, and row counts.

## Build

The builder needs a valid WS4 carbon package, a dataset for the track/age
inventory and treatment transitions, libcbm, and the WS4 package on
`PYTHONPATH`.

```bash
python scripts/build_state_cache.py \
  --dataset /path/to/compiled-dataset \
  --package /path/to/femic-carbon-package \
  --hwp-config config/carbon/hwp.bc.yaml \
  --years 50 \
  --offsets 0-49 \
  --workers 64 \
  --out cache/tsa41-cc-offsets
```

The build is parallel across stand states. It writes one file per chain offset
and clears the in-process cache between offsets so memory stays bounded.

Use `--limit` for a small pilot and `--offsets 0,1,2` for a bounded check.

## Client

```python
from fresh_cbm import StateCache

cache = StateCache.load("cache/tsa41-cc-offsets")
row = cache.lookup(track_id=12, age=80, chain_offset=0)
print(row.shape)  # (years + 1, accounts)
```

## Validation

Every cache must record a source manifest and be validated by comparing a
sample of rows against a fresh exact `CarbonLedger` run at the same state. Exact
`ws4 carbon` replay remains the reporting authority.

## Status

This repository is new. The first target is TSA41, one-event `CC@offset` chains,
actual track/age states. The full pool/flux tables are optional; the account
table is the default because it is what carbon targets consume.

Validation contract
===================

The cache is useful only if its identity and rows are checked.

Manifest identity
-----------------

``fresh_cbm.schema.validate_manifest`` enforces:

- schema name ``fresh-cbm-state-v1``
- required dataset, package, fingerprint, CBM defaults, libcbm version
- positive year count and state count
- dtype ``float32`` or ``float64``
- unique accounts, offsets, and files

Exactness
---------

The builder uses the exact WS4 ``CarbonLedger`` stand-state path. The validator
recomputes sampled states with the same path and requires a zero error.

Consumer contract
-----------------

``ws4 carbon-removal --state-cache`` reads carbon cells from the cache and
non-carbon cells from the WS4 simulator. The current chain must be empty or one
``CC`` event, and every block track/age/offset must exist. Exact
``ws4 carbon`` replay remains the reported authority.

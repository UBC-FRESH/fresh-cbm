Architecture and data flow
==========================

The package has four layers: source tables, builder, state cache, and consumer.

Data flow
---------

.. code-block:: text

   carbon package --------+
   compiled dataset ------+--> builder (WS4 CarbonLedger) --> state arrays
   treatments/transitions +                                      |
   HWP config                                                    v
                                                        manifest + index
                                                               |
                                                               v
                                                      fresh_cbm.StateCache
                                                               |
                                  +----------------------------+------------------+
                                  |                                               |
                                  v                                               v
                        WS4 state-cache consumer                     direct client lookup
                                  |
                                  v
                       block area weighting + target cells
                                  |
                                  v
                         exact ws4 carbon replay

Components
----------

Builder
~~~~~~~

`scripts/build_state_cache.py` uses WS4's exact `CarbonLedger` stand-state path.
It enumerates the declared track/age states, prices each chain offset, and writes
one array per chain.

The builder is intentionally outside the runtime package. It needs WS4 and
libcbm; the client does not.

Cache
~~~~~

A cache directory contains:

- `manifest.json` — versioned identity and schema;
- `index.parquet` — row id to track/age mapping;
- `values/empty.npy` — untreated states;
- `values/offset_XX.npy` — one-event `CC` states.

Each value array has shape `(states, years + 1, accounts)`.

Client
~~~~~~

`fresh_cbm.StateCache` validates the manifest, maps `(track_id, age)` to a row,
and reads the appropriate memmap. It returns account vectors in the manifest's
declared order.

Consumer
~~~~~~~~

WS4's `ws4 carbon-removal --state-cache` combines cached carbon cells with
non-carbon cells from the WS4 simulator. It creates an exact per-block effect
table, searches it, and replays the winning schedule through the exact carbon
path.

State identity
--------------

The logical key is:

.. code-block:: text

   package fingerprint
   + track/classifier identity
   + age
   + treatment chain
   + boundary variant
   + HWP / fertilization config
   + CBM defaults and libcbm version
   + horizon and account schema

The manifest is the machine-readable identity. A consumer must reject a cache
that does not match its run.

Exactness and fallback
----------------------

The cache is exact for its declared state family. It is not a complete model of
all possible states. A consumer must fall back to libcbm or the exact WS4 ledger
when:

- a state, age, track, or offset is missing;
- a chain has unsupported events;
- the package or CBM defaults differ;
- the account schema or horizon differs; or
- the cache file fails checksum or shape validation.

Performance model
-----------------

The cache changes the cost profile:

- build: one-time CBM state construction, parallel over states;
- lookup: metadata validation, a memmap read, and array indexing;
- consumer: block area sums and target-cell projection.

For the published TSA41 cache, the full landscape lookup removed a 976 s table
build. The remaining full-run cost was exact replay.

Security and provenance
-----------------------

- Release values are hashed in `SHA256SUMS`.
- The manifest records package fingerprint, CBM defaults hash, and libcbm
  version.
- Public manifests must not contain machine-specific paths or private data.
- The client validates the schema but does not replace a checksum audit.

Related pages
-------------

- :doc:`../guides/cache-format`
- :doc:`../reference/validation`
- :doc:`../guides/applications`

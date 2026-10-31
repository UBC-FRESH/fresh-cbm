Cache format
============

A cache is a directory with a manifest, a state index, and one NumPy array per
chain offset.

.. code-block:: text

   manifest.json
   index.parquet
   values/empty.npy
   values/offset_00.npy
   ...
   values/offset_49.npy

``manifest.json`` is validated by the packaged JSON Schema. It records the
source package, package fingerprint, libcbm version, CBM defaults hash, years,
dtype, account names, offsets, state count, and file list.

``index.parquet`` maps a row id to ``track_id``, ``track_name``, and ``age``.
Every value array has shape ``(states, years + 1, accounts)``. The empty chain
is stored separately.

The cache is exact for the manifest identity. Any mismatch must fall back to
WS4's exact carbon ledger or a fresh libcbm run.

State, not blocks
-----------------

CBM is aspatial. A cache row is a per-hectare stand state. Block effects are
area-weighted sums of state rows applied by the consumer. The cache does not
contain block topology, adjacency, or planning targets.

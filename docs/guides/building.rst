Building a cache
================

The builder requires WS4 with the ``carbon`` extra, a compiled dataset for the
track/age inventory and treatment transitions, a carbon package, and libcbm.

.. code-block:: bash

   PYTHONPATH=/path/to/ws4 python scripts/build_state_cache.py \
     --dataset /path/to/compiled-dataset \
     --package /path/to/femic-carbon-package \
     --hwp-config /path/to/hwp.bc.yaml \
     --years 50 --offsets 0-49 --workers 64 \
     --out cache/tsa41-cc-offsets

Use ``--limit`` and ``--offsets`` for a pilot. The builder clears the
in-process state cache between offsets so memory stays bounded.

Validation
----------

.. code-block:: bash

   python scripts/validate_cache.py \
     --cache cache/tsa41-cc-offsets \
     --dataset /path/to/compiled-dataset \
     --package /path/to/femic-carbon-package \
     --hwp-config /path/to/hwp.bc.yaml \
     --samples 8

The validator compares sampled state/offset rows with a fresh exact
``CarbonLedger`` state. It must report zero error before release.

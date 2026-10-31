Building a cache
================

The builder requires WS4 with the ``carbon`` extra, a compiled dataset for the
track/age inventory and treatment transitions, a carbon package, and libcbm.

.. code-block:: bash

   fresh-cbm-build \
     --dataset /path/to/compiled-dataset \
     --package /path/to/femic-carbon-package \
     --hwp-config /path/to/hwp.bc.yaml \
     --years 50 --offsets 0-49 --workers 64 \
     --out cache/tsa41-cc-offsets

The builder still needs WS4 with the ``carbon`` extra on ``PYTHONPATH``. The
console command is installed by ``pip install -e .``.

Use ``--limit`` and ``--offsets`` for a pilot. The builder clears the
in-process state cache between offsets so memory stays bounded.

Validation
----------

.. code-block:: bash

   fresh-cbm-validate \
     --cache cache/tsa41-cc-offsets \
     --dataset /path/to/compiled-dataset \
     --package /path/to/femic-carbon-package \
     --hwp-config /path/to/hwp.bc.yaml \
     --samples 8

The validator compares sampled state/offset rows with a fresh exact
``CarbonLedger`` state. It must report zero error before release.

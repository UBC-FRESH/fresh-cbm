Benchmarks
==========

The benchmarks separate one-time cache construction from repeated use.

Published caches
----------------

| Cache | States | Accounts | Offsets | Size | Build |
| --- | ---: | ---: | ---: | ---: | ---: |
| TSA41 | 5,273 | 26 | 50 | 2.85 GB | 10,991 s |
| TSA08 | 3,761 | 26 | 50 | 2.03 GB | 7,552 s |

Consumer measurements
---------------------

Measured with `fresh-cbm-bench`, one target cell
(`carbon.system.total` at year 49), all blocks in the landscape, 100 random
lookups:

| Cache | Blocks | Load | Median lookup | Effect projection |
| --- | ---: | ---: | ---: | ---: |
| TSA41 | 148,828 | 0.018 s | 0.85 ms | **2.33 s** |
| TSA08 | 371,565 | 0.032 s | 1.18 ms | **4.96 s** |

The projection includes fragment area weighting and state lookup. It is the
phase that replaces repeated `CarbonLedger.prepare` work in the consumer.

Reproduce
---------

.. code-block:: bash

   fresh-cbm-bench \
     --cache cache/tsa41-cc-offsets \
     --dataset /path/to/tsa41-p120-matrix-full \
     --account carbon.system.total \
     --year 49 \
     --offset 0 \
     --repeats 100 \
     --out notes/reports/benchmark-tsa41.json

The JSON record contains the full measurements.

Limits
------

- lookup timing includes the memmap open/read path used by the client;
- the projection covers carbon cells only;
- build time is reported in the cache manifest, not rerun by the benchmark;
- exact whole-schedule WS4 replay is outside this benchmark.

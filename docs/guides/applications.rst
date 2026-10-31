Applications and worked example
================================

This page shows how the cache is used and what it does not decide.

Worked example: TSA41
---------------------

The first public cache is the TSA41 one-event family.

Build inputs
~~~~~~~~~~~~

- compiled TSA41 dataset;
- FEMIC carbon package;
- public-default HWP configuration;
- 50 years;
- untreated plus `CC` at every offset 0–49.

Release
~~~~~~~

`v0.1.0-tsa41` contains:

- 5,273 actual track/age states;
- 51 chains per state;
- 26 carbon accounts;
- float64 values;
- 2.85 GB across 55 release assets.

The cache is public:

https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa41

Consumer run
~~~~~~~~~~~~

A 5,000-block WS4 removal search used the cache as follows:

.. code-block:: bash

   ws4 carbon-removal \
     --dataset /path/to/tsa41-5k-dataset \
     --package /path/to/tsa41-package \
     --schedule /path/to/initial-cc0.schedule.csv \
     --targets /path/to/targets.yaml \
     --years 50 \
     --hwp-config /path/to/hwp.bc.yaml \
     --state-cache /path/to/fresh-cbm-cache \
     --solver auto \
     --out runs/removal

The effect-table build was effectively zero; the 5k run took about 50 s
including exact replay, compared with about 207 s without the cache.

A full 148,828-block run reproduced the same exact schedule and
**213,103,705 tCO2e** result. The table-build phase disappeared; the remaining
time was dominated by exact replay.

These numbers are **validation evidence for the cache**, not a policy
recommendation.

Typical workflow
----------------

.. code-block:: text

   package + transitions + age family
                   |
                   v
             build state cache
                   |
                   v
          validate against exact ledger
                   |
                   v
          package checksums + release
                   |
                   v
   consumer: lookup -> block area sum -> target cells
                   |
                   v
             exact final replay

Build once, then reuse while the cache identity is unchanged.

What invalidates a cache
------------------------

A cache is tied to:

- carbon package fingerprint;
- CBM defaults hash;
- libcbm version;
- treatment transition set;
- track/age/boundary state family;
- HWP and fertilization configuration;
- horizon and account schema;
- dtype and array layout.

Changing targets does **not** invalidate the state cache. Changing the package,
configuration, state family, or account layout does.

FAQ
---

**Does this replace libcbm?**

No. It stores libcbm outputs for a declared family. Uncovered states fall back to
libcbm or the exact WS4 ledger.

**Can I use it for another TSA?**

Yes, by building a new cache for that package and landscape. The format and
client are generic; the published TSA41 release is one product.

**Does it support multi-event chains?**

Not yet. The published family is untreated plus one `CC` event. Multi-event
chains need a larger state family and a new builder invocation.

**Does it include spatial constraints?**

No. Block topology, adjacency, openings, routes, and patch rules stay in WS4.

**Is it a learned model?**

No. Every row is an exact libcbm account vector.

**Why not use an ML surrogate?**

A bounded surrogate experiment showed about 12% error on cumulative emissions
and HWP carbon, which is larger than the optimization signal. The exact cache is
both more accurate and already fast.

**Can I commit the cache to git?**

Do not commit multi-GB arrays to ordinary history. Use release assets or LFS and
publish the checksums and release record.

**What remains expensive?**

The final exact whole-schedule replay in WS4. The state cache removes repeated
state construction, not the authoritative replay.

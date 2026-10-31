Context and target applications
================================

`fresh-cbm` exists because the same deterministic libcbm stand-state calculation
is repeated across analyses, scenarios, and optimizer iterations. The cache
stores those exact states once and turns later carbon evaluation into a keyed
array lookup.

The problem
-----------

libcbm is exact and aspatial: a stand's trajectory is determined by its track,
initial age, treatment chain, CBM defaults, and the package configuration. That
makes it a good fit for caching. It is also expensive to initialize a model for
every state on every search move.

In the TSA41 work, building the removal-effect table through the ordinary
`CarbonLedger` path took:

- about 156 s for a 5,000-block sample; and
- about 976 s for the full 148,828-block landscape.

The cache removes that repeated state construction. It does not approximate it.

What this package is
--------------------

`fresh-cbm` is a **package-level, exact stand-state cache**:

- one row per `(track, age, chain)` state;
- per-hectare carbon accounts for every stored year;
- a versioned manifest that pins the package, CBM defaults, libcbm version,
  horizon, dtype, accounts, and offsets;
- a small Python client for lookup; and
- a builder, validator, and release tooling for producing cache products.

A block effect is produced by the consumer as an area-weighted sum of state
rows. The cache itself contains no blocks, topology, or planning targets.

What it is not
--------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Not this
     - Why
   * - A learned surrogate
     - Every cached value is an exact libcbm output. Missing states must fall
       back to libcbm, not to interpolation.
   * - A spatial model
     - CBM is aspatial. Topology, adjacency, openings, and routes belong to the
       consuming model.
   * - A policy recommendation
     - The cache is modelling infrastructure. Policy interpretation belongs in
       the project that consumes the cache.
   * - A full libcbm replacement
     - The cache covers only the declared state family. New packages, chains,
       ages, or configurations need a new or extended cache.
   * - A block inventory
     - Block area and fragment mapping are dataset-specific and stay outside the
       state cache.

Who it is for
-------------

- **WS4/FEMIC developers** who need to remove repeated CBM state construction
  from carbon optimization and analysis.
- **Carbon analysts** running repeated scenarios on a fixed package and state
  family.
- **Research software engineers** publishing reproducible carbon state
  products.
- **Collaborators and students** who need an inspectable, exact carbon state
  table without running libcbm first.
- **Coding agents** that need a stable contract and an explicit fallback path.

Target applications
-------------------

1. **WS4 carbon removal optimization**

   `ws4 carbon-removal --state-cache PATH` reads carbon cells from the cache and
   non-carbon cells from the WS4 simulator. The exact effect table is then
   searched with the GPU population or the MILP knapsack. This is the first
   production consumer.

2. **Repeated scenario and sensitivity analyses**

   Build the state family once, then evaluate many schedules, targets, or
   policies against the same package without rebuilding CBM state.

3. **Multi-TSA cache products**

   Each cache is a package-scoped artifact with its own manifest. TSA-specific
   products can be published together as long as each names its package and
   configuration.

4. **Regression and validation fixtures**

   The exact state table makes it possible to test carbon consumers against a
   fixed, inspectable state set instead of a live model build.

5. **Teaching and reproducibility**

   A cache release records the exact engine and package identity behind every
   value, which is useful when a result must be reproduced later.

When to use it
--------------

Use the cache when most of the following are true:

- the same package, CBM defaults, HWP configuration, and horizon will be reused;
- the required state family is known and bounded;
- exactness matters more than covering arbitrary future treatment chains;
- the storage and one-time build cost are acceptable; and
- you can pin the cache identity in the consuming result.

Run libcbm directly when the analysis is a one-off, the state family is unknown,
or the package/configuration changes on every run.

Scope boundary
--------------

The cache covers **stand states**, not landscapes. A consumer still owns:

- block and fragment inventory;
- area weighting;
- spatial and operational constraints;
- target definitions;
- final exact replay and reporting.

The first published family is TSA41, actual track/age states, untreated plus one
`CC` event at offsets 0–49. Multi-event chains, fertilization variants, and other
packages require additional caches.

A worked example is in :doc:`applications`. The data contract is in
:doc:`cache-format`; the internal flow is in :doc:`../reference/architecture`.

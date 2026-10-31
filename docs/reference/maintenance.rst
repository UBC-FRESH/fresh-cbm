Maintenance and compatibility
=============================

`fresh-cbm` is maintained by the UBC FRESH Lab. This page records the review
cadence, compatibility rules, and cache rebuild triggers.

Review cadence
--------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Cadence
     - Review
   * - Monthly
     - CI health, dependency and security updates, open issues and pull requests,
       broken docs links, release-asset availability, and cache verification.
   * - Quarterly
     - libcbm and CBM-defaults versions, package fingerprints, storage growth,
       compatibility/deprecation status, and docs accuracy.
   * - Annual
     - Full cache rebuild plan, retention/removal of obsolete releases, and
       maintainer ownership.
   * - Event-driven
     - Rebuild when a manifest trigger changes; triage security or correctness
       reports immediately.

Owners
------

The UBC FRESH Lab maintainers own the package and release decisions. A change to
the cache schema, a new public cache family, a PyPI publication, or a deprecation
needs maintainer approval.

Compatibility
-------------

- The package follows semantic versioning.
- `fresh-cbm-state-v1` is the current cache schema.
- A schema change that is not backward compatible needs a new schema name and a
  migration note.
- The client must keep reading legacy manifests that omit optional metadata until
  a documented deprecation date.
- A removed field or command gets a deprecation note in the changelog and one
  release of overlap where practical.
- Exact values are not silently redefined. If a source model changes, publish a
  new cache identity and release rather than overwriting an old one.

Cache rebuild triggers
----------------------

Rebuild a cache when any of these change:

- carbon package fingerprint;
- CBM defaults hash;
- libcbm version;
- treatment transition table;
- track/classifier/boundary inventory;
- yield curves;
- HWP or fertilization configuration;
- years, account schema, dtype, or array layout;
- chain family.

Changing consumer targets does not require a state-cache rebuild.

Cache lifecycle
---------------

1. Build with `fresh-cbm-build`.
2. Validate sampled states with `fresh-cbm-validate`.
3. Package with `fresh-cbm-package`.
4. Publish assets under a versioned release.
5. Verify with `fresh-cbm-verify`.
6. Record the release identity and known gaps.
7. Retire only with a changelog note and maintainer approval.

Triage
------

- Correctness or integrity reports: reproduce, verify the cache identity, and
  block further use of the affected release if needed.
- Compatibility reports: record the failing client/cache pair and preserve a
  legacy read path.
- Feature requests: add to the roadmap; do not silently expand the chain family.
- Security reports: follow the repository security policy and avoid publishing
  details before a fix.

Release and data safety
-----------------------

- Do not commit multi-GB cache arrays to ordinary git history.
- Use release assets or LFS, with checksums.
- Keep credentials, private data, and machine-specific paths out of manifests,
  docs, and release notes.
- Verify the public release after any settings or storage change.

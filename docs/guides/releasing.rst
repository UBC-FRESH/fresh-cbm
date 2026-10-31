Releasing a cache
=================

1. Run the exact validator.
2. Write checksums and a release record:

   .. code-block:: bash

      python scripts/package_cache.py --cache cache/tsa41-cc-offsets

3. Upload ``manifest.json``, ``index.parquet``, every ``values/*.npy``,
   ``SHA256SUMS``, and ``release.json`` as release assets.
4. Record the package fingerprint, CBM defaults hash, libcbm version, dtype,
   horizon, accounts, and state count in the release notes.

Do not commit multi-GB arrays to ordinary git history. Release assets or LFS are
the supported storage paths. The manifest paths are repository-relative; local
machine paths must not be published.

Releasing a cache
=================

1. Run the exact validator.
2. Write checksums and a release record:

   .. code-block:: bash

      fresh-cbm-package --cache cache/tsa41-cc-offsets

3. Upload ``manifest.json``, ``index.parquet``, every ``values/*.npy``,
   ``SHA256SUMS``, and ``release.json`` as release assets.
4. Record the package fingerprint, CBM defaults hash, libcbm version, dtype,
   horizon, accounts, and state count in the release notes.
5. Verify the uploaded cache offline:

   .. code-block:: bash

      fresh-cbm-verify --cache cache/tsa41-cc-offsets

Package release
---------------

The package release is separate from the cache release tags.

.. code-block:: bash

   python -m pip install build
   python -m build
   fresh-cbm-verify --cache cache/tsa41-cc-offsets
   gh release create v0.2.0 \
     --title "fresh-cbm v0.2.0" \
     --notes-file notes/releases/v0.2.0.md \
     dist/*.whl dist/*.tar.gz

The tag must point at the release commit. PyPI publication is a separate
maintainer decision; do not publish externally without explicit approval.

Do not commit multi-GB arrays to ordinary git history. Release assets or LFS are
the supported storage paths for caches. The manifest paths are repository-relative; local
machine paths must not be published.

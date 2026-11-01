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

Trusted publishing
------------------

The repository uses GitHub OIDC trusted publishing. No PyPI token is stored in
the repository.

- workflow: `.github/workflows/release.yaml`
- environments: `testpypi` and `pypi`
- project: `fresh-cbm`

Run it from `main`:

.. code-block:: bash

   gh workflow run release.yaml --ref main -f target=testpypi
   gh workflow run release.yaml --ref main -f target=pypi

The workflow builds the sdist and wheel, checks them with `twine`, and publishes
with `pypa/gh-action-pypi-publish`.

Verify the published installs:

.. code-block:: bash

   python -m venv /tmp/pypi-venv
   /tmp/pypi-venv/bin/pip install fresh-cbm==0.2.0
   /tmp/pypi-venv/bin/fresh-cbm-verify --help

   python -m venv /tmp/testpypi-venv
   /tmp/testpypi-venv/bin/pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     fresh-cbm==0.2.0
   /tmp/testpypi-venv/bin/fresh-cbm-verify --help

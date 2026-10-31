"""Tests for release packaging."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_cbm import release


def _cache(root: Path) -> None:
    (root / "values").mkdir(parents=True)
    np.save(root / "values" / "empty.npy", np.zeros((1, 2, 1)))
    pd.DataFrame({"state_id": [0], "track_id": [1], "track_name": ["a"], "age": [10]}).to_parquet(
        root / "index.parquet", index=False
    )
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "dataset": "test",
        "package": "test",
        "package_fingerprint": "test",
        "libcbm_version": "2",
        "cbm_defaults_sha256": "d",
        "years": 1,
        "dtype": "float64",
        "accounts": ["a"],
        "offsets": [0],
        "empty": True,
        "states": 1,
        "files": ["values/empty.npy"],
    }
    (root / "manifest.json").write_text(json.dumps(manifest))


def test_package_cache_writes_checksums(tmp_path: Path) -> None:
    """The release command validates files and writes both records."""
    root = tmp_path / "cache"
    _cache(root)
    assert release.main(["--cache", str(root)]) == 0
    assert (root / "SHA256SUMS").is_file()
    assert json.loads((root / "release.json").read_text())["states"] == 1

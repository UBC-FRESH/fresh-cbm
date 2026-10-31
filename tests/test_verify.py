"""Tests for offline cache verification."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fresh_cbm import release
from fresh_cbm.verify import main, verify_cache


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


def test_verify_checks_shape_and_release(tmp_path: Path) -> None:
    """A packaged cache verifies with checksums and release metadata."""
    root = tmp_path / "cache"
    _cache(root)
    assert release.main(["--cache", str(root)]) == 0
    report = verify_cache(root)
    assert report["states"] == 1
    assert report["release_checked"] is True


def test_verify_rejects_tampering_and_missing_checksums(tmp_path: Path) -> None:
    """Tampering and a missing checksum file fail verification."""
    root = tmp_path / "cache"
    _cache(root)
    with pytest.raises(ValueError, match="checksum file"):
        verify_cache(root)
    release.main(["--cache", str(root)])
    (root / "values" / "empty.npy").write_bytes(b"bad")
    with pytest.raises(ValueError, match="checksum"):
        verify_cache(root)


def test_verify_command_reports_errors(tmp_path: Path) -> None:
    """The console verifier returns one on a bad cache."""
    assert main(["--cache", str(tmp_path / "missing")]) == 1

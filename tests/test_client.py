"""Tests for the fresh-cbm state cache client."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fresh_cbm import StateCache


def test_lookup_reads_the_offset_file(tmp_path: Path) -> None:
    """A state lookup reads the right offset row and account column."""
    root = tmp_path / "cache"
    (root / "values").mkdir(parents=True)
    index = pd.DataFrame(
        {
            "state_id": [0, 1],
            "track_id": [7, 7],
            "track_name": ["a", "a"],
            "age": [10, 20],
        }
    )
    index.to_parquet(root / "index.parquet", index=False)
    values = np.arange(2 * 3 * 2, dtype=np.float64).reshape(2, 3, 2)
    np.save(root / "values" / "offset_00.npy", values)
    np.save(root / "values" / "empty.npy", values + 100.0)
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "dataset": "test",
        "package": "test",
        "package_fingerprint": "test",
        "libcbm_version": "test",
        "cbm_defaults_sha256": "test",
        "years": 2,
        "dtype": "float64",
        "accounts": ["yield", "carbon"],
        "offsets": [0],
        "empty": True,
        "states": 2,
        "files": ["values/empty.npy", "values/offset_00.npy"],
    }
    (root / "manifest.json").write_text(__import__("json").dumps(manifest))
    cache = StateCache.load(root)
    np.testing.assert_array_equal(cache.lookup(track_id=7, age=20, chain_offset=0), values[1])
    np.testing.assert_array_equal(cache.account(7, 10, -1, "carbon"), values[0, :, 1] + 100.0)


def test_lookup_rejects_unknown_state_and_account(tmp_path: Path) -> None:
    """Unknown states and accounts fail clearly."""
    root = tmp_path / "cache"
    (root / "values").mkdir(parents=True)
    np.save(root / "values" / "empty.npy", np.zeros((1, 3, 1)))
    index = pd.DataFrame({"state_id": [0], "track_id": [7], "track_name": ["a"], "age": [10]})
    index.to_parquet(root / "index.parquet", index=False)
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "dataset": "test",
        "package": "test",
        "package_fingerprint": "test",
        "libcbm_version": "test",
        "cbm_defaults_sha256": "test",
        "years": 2,
        "dtype": "float64",
        "accounts": ["yield"],
        "offsets": [0],
        "empty": True,
        "states": 1,
        "files": ["values/empty.npy"],
    }
    (root / "manifest.json").write_text(__import__("json").dumps(manifest))
    cache = StateCache.load(root)
    assert cache.years == 2
    np.testing.assert_array_equal(cache.lookup_state(0, -1), np.zeros((3, 1)))
    with pytest.raises(KeyError, match="state not in cache"):
        cache.lookup(8, 10)
    with pytest.raises(KeyError, match="account not in cache"):
        cache.account(7, 10, -1, "carbon")


def test_accounts_rejects_a_malformed_manifest() -> None:
    """A manifest with non-list accounts is rejected by the property."""
    cache = StateCache(
        root=Path("."),
        manifest={"accounts": "not-a-list", "years": 2},
        index=pd.DataFrame(),
    )
    with pytest.raises(ValueError, match="accounts"):
        _ = cache.accounts


def _minimal_cache(root: Path, *, shape: tuple[int, ...] = (1, 3, 1)) -> None:
    """Write a minimal valid cache at ``root``."""
    (root / "values").mkdir(parents=True)
    np.save(root / "values" / "empty.npy", np.zeros(shape))
    np.save(root / "values" / "offset_00.npy", np.ones(shape))
    index = pd.DataFrame({"state_id": [0], "track_id": [7], "track_name": ["a"], "age": [10]})
    index.to_parquet(root / "index.parquet", index=False)
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "dataset": "test",
        "package": "test",
        "package_fingerprint": "test",
        "libcbm_version": "test",
        "cbm_defaults_sha256": "test",
        "years": 2,
        "dtype": "float64",
        "accounts": ["yield"],
        "offsets": [0],
        "empty": True,
        "states": 1,
        "files": ["values/empty.npy", "values/offset_00.npy"],
    }
    (root / "manifest.json").write_text(__import__("json").dumps(manifest))


def test_load_rejects_a_truncated_array(tmp_path: Path) -> None:
    """A shape that does not match the manifest fails at load time."""
    root = tmp_path / "cache"
    _minimal_cache(root, shape=(1, 2, 1))
    with pytest.raises(ValueError, match="expected"):
        StateCache.load(root)


def test_checksum_verification_detects_tampering(tmp_path: Path) -> None:
    """A changed value file fails checksum verification."""
    root = tmp_path / "cache"
    _minimal_cache(root)
    checksum = root / "SHA256SUMS"
    empty = root / "values" / "empty.npy"
    digest = __import__("hashlib").sha256(empty.read_bytes()).hexdigest()
    checksum.write_text(f"{digest}  values/empty.npy\n")
    cache = StateCache.load(root)
    cache.verify_checksums()
    empty.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        cache.verify_checksums()

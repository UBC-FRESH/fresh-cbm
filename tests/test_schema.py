"""Tests for manifest schema validation."""

from __future__ import annotations

import pytest
from fresh_cbm.schema import validate_manifest

BASE = {
    "schema": "fresh-cbm-state-v1",
    "dataset": "test",
    "package": "test",
    "package_fingerprint": "abc",
    "libcbm_version": "2.10.2",
    "cbm_defaults_sha256": "def",
    "years": 50,
    "dtype": "float64",
    "accounts": ["carbon.system.total"],
    "offsets": [0],
    "empty": True,
    "states": 1,
    "files": ["values/empty.npy"],
}


def test_manifest_accepts_the_minimal_contract() -> None:
    """A complete minimal manifest validates."""
    assert validate_manifest(BASE)["schema"] == "fresh-cbm-state-v1"


def test_manifest_rejects_bad_dtype() -> None:
    """A malformed dtype is rejected."""
    with pytest.raises(ValueError, match="float32"):
        validate_manifest({**BASE, "dtype": "float16"})


def test_manifest_rejects_missing_fields() -> None:
    """Required fields cannot be omitted."""
    broken = dict(BASE)
    del broken["accounts"]
    with pytest.raises(ValueError, match="accounts"):
        validate_manifest(broken)

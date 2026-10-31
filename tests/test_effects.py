"""Tests for the block/fragment effect projection."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fresh_cbm import StateCache
from fresh_cbm.effects import build_block_effects


def _cache(root: Path) -> StateCache:
    (root / "values").mkdir(parents=True)
    # Two states, two accounts, three years.
    empty = np.array(
        [
            [[10.0, 100.0], [11.0, 101.0], [12.0, 102.0]],
            [[20.0, 200.0], [21.0, 201.0], [22.0, 202.0]],
        ]
    )
    current = empty - 5.0
    np.save(root / "values" / "empty.npy", empty)
    np.save(root / "values" / "offset_00.npy", current)
    pd.DataFrame(
        {
            "state_id": [0, 1],
            "track_id": [1, 2],
            "track_name": ["a", "b"],
            "age": [10, 20],
        }
    ).to_parquet(root / "index.parquet", index=False)
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "dataset": "test",
        "package": "test",
        "package_fingerprint": "test",
        "libcbm_version": "test",
        "cbm_defaults_sha256": "test",
        "years": 2,
        "dtype": "float64",
        "accounts": ["carbon.system.total", "other"],
        "offsets": [0],
        "empty": True,
        "chain_family": {
            "treatment": "CC",
            "events": 1,
            "offsets": [0],
            "allow_empty": True,
        },
        "states": 2,
        "files": ["values/empty.npy", "values/offset_00.npy"],
    }
    (root / "manifest.json").write_text(json.dumps(manifest))
    return StateCache.load(root)


def test_block_effects_sum_multiple_fragments(tmp_path: Path) -> None:
    """Blocks aggregate their fragments and apply area weights."""
    cache = _cache(tmp_path / "cache")
    fragments = pd.DataFrame(
        {
            "block_id": [1, 1, 2],
            "track_id": [1, 2, 2],
            "age": [10, 20, 20],
            "area_ha": [2.0, 1.0, 3.0],
        }
    )
    effects = build_block_effects(
        cache,
        fragments,
        {1: (("CC", 0),), 2: (("CC", 0),)},
        [(0, "carbon.system.total")],
    )
    assert effects.base[0] == 2 * 10 + 1 * 20 + 3 * 20
    assert effects.effects[:, 0].tolist() == [-15.0, -15.0]
    assert effects.totals({1: True, 2: False})[(0, "carbon.system.total")] == 85.0


def test_block_effects_reject_bad_inputs(tmp_path: Path) -> None:
    """Missing states, bad cells, and unknown chains fail clearly."""
    cache = _cache(tmp_path / "cache")
    fragments = pd.DataFrame({"block_id": [1], "track_id": [9], "age": [10], "area_ha": [1.0]})
    with pytest.raises(ValueError, match="track/age"):
        build_block_effects(cache, fragments, {1: (("CC", 0),)}, [(0, "carbon.system.total")])
    with pytest.raises(ValueError, match="account"):
        build_block_effects(
            cache,
            fragments.assign(track_id=1),
            {1: (("CC", 0),)},
            [(0, "missing")],
        )
    with pytest.raises(ValueError, match="outside"):
        build_block_effects(cache, fragments.assign(track_id=1), {1: (("CC", 1),)}, [(0, "other")])

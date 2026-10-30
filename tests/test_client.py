"""Tests for the fresh-cbm state cache client."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
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
        "years": 2,
        "accounts": ["yield", "carbon"],
        "offsets": [0],
    }
    (root / "manifest.json").write_text(__import__("json").dumps(manifest))
    cache = StateCache.load(root)
    np.testing.assert_array_equal(cache.lookup(track_id=7, age=20, chain_offset=0), values[1])
    np.testing.assert_array_equal(cache.account(7, 10, -1, "carbon"), values[0, :, 1] + 100.0)

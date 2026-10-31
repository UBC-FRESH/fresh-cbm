"""Tests for cache benchmarks."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fresh_cbm.benchmark import benchmark_cache, main


def _cache(root: Path) -> None:
    (root / "values").mkdir(parents=True)
    values = np.zeros((1, 3, 1))
    np.save(root / "values" / "empty.npy", values)
    np.save(root / "values" / "offset_00.npy", values)
    pd.DataFrame({"state_id": [0], "track_id": [1], "track_name": ["a"], "age": [10]}).to_parquet(
        root / "index.parquet", index=False
    )
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "dataset": "test",
        "package": "test",
        "package_fingerprint": "test",
        "libcbm_version": "test",
        "cbm_defaults_sha256": "test",
        "years": 2,
        "dtype": "float64",
        "accounts": ["carbon.system.total"],
        "offsets": [0],
        "empty": True,
        "chain_family": {
            "treatment": "CC",
            "events": 1,
            "offsets": [0],
            "allow_empty": True,
        },
        "states": 1,
        "files": ["values/empty.npy", "values/offset_00.npy"],
    }
    (root / "manifest.json").write_text(json.dumps(manifest))


def test_benchmark_records_lookup_and_projection(tmp_path: Path) -> None:
    """The benchmark reports cache scale and projection timing."""
    root = tmp_path / "cache"
    _cache(root)
    fragments = pd.DataFrame({"block_id": [1], "track_id": [1], "age": [10], "area_ha": [1.0]})
    result = benchmark_cache(
        root,
        fragments,
        {1: (("CC", 0),)},
        [(0, "carbon.system.total")],
        repeats=3,
    )
    assert result.states == 1
    assert result.blocks == 1
    assert result.lookup_repeats >= 1
    assert result.bytes > 0


def test_benchmark_command_writes_json(tmp_path: Path) -> None:
    """The console benchmark reads fragments and writes a JSON record."""
    root = tmp_path / "cache"
    _cache(root)
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    pd.DataFrame({"block_id": [1], "track_id": [1], "age": [10], "area_ha": [1.0]}).to_parquet(
        dataset / "fragments.parquet", index=False
    )
    out = tmp_path / "bench.json"
    assert (
        main(
            [
                "--cache",
                str(root),
                "--dataset",
                str(dataset),
                "--year",
                "0",
                "--repeats",
                "2",
                "--out",
                str(out),
            ]
        )
        == 0
    )
    assert json.loads(out.read_text())["states"] == 1


def test_benchmark_help() -> None:
    """The command documents its options."""
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0

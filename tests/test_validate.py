"""Tests for the exact cache validator command."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
import pytest
from fresh_cbm import validate


class _FakeLedger:
    """A ledger that returns the same zero accounts as the fixture cache."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def _unit_accounts(
        self, track: int, age: int, chain: tuple[tuple[str, int], ...]
    ) -> dict[tuple[int, str], float]:
        return {(0, "carbon.system.total"): 0.0}


def _install_ws4(monkeypatch: pytest.MonkeyPatch) -> None:
    modules = {
        "ws4": ModuleType("ws4"),
        "ws4.carbon": ModuleType("ws4.carbon"),
        "ws4.carbon.hwp": ModuleType("ws4.carbon.hwp"),
        "ws4.carbon.ledger": ModuleType("ws4.carbon.ledger"),
        "ws4.carbon.package": ModuleType("ws4.carbon.package"),
    }
    setattr(modules["ws4.carbon.hwp"], "load_hwp_config", lambda path: None)  # noqa: B010 - dynamic fake module
    setattr(modules["ws4.carbon.ledger"], "CarbonLedger", _FakeLedger)  # noqa: B010 - dynamic fake module
    setattr(modules["ws4.carbon.package"], "load_carbon_package", lambda path: object())  # noqa: B010 - dynamic fake module
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)


def test_validate_command_checks_a_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The console validator compares a cache with the exact ledger."""
    _install_ws4(monkeypatch)
    root = tmp_path / "cache"
    (root / "values").mkdir(parents=True)
    np.save(root / "values" / "empty.npy", np.zeros((1, 3, 1)))
    np.save(root / "values" / "offset_00.npy", np.zeros((1, 3, 1)))
    pd.DataFrame({"state_id": [0], "track_id": [7], "track_name": ["a"], "age": [10]}).to_parquet(
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
        "states": 1,
        "files": ["values/empty.npy", "values/offset_00.npy"],
    }
    (root / "manifest.json").write_text(json.dumps(manifest))
    assert (
        validate.main(
            [
                "--cache",
                str(root),
                "--dataset",
                "dataset",
                "--package",
                "package",
                "--samples",
                "1",
                "--ws4-path",
                str(tmp_path),
                "--workers",
                "1",
            ]
        )
        == 0
    )

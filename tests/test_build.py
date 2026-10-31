"""Tests for the package build entry point."""

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path
from types import ModuleType

import pandas as pd
import pytest
from fresh_cbm import build


class _FakeLedger:
    """A one-state ledger used to exercise the builder's file path."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.fragments = pd.DataFrame({"track_id": [1], "age": [10], "area_ha": [1.0]})
        self.tracks = pd.DataFrame({"track_id": [1], "name": ["a"]})
        self._unit_cache: dict[
            tuple[int, int, tuple[tuple[str, int], ...]], dict[tuple[int, str], float]
        ] = {}
        self._cache: dict[object, object] = {}

    def _prepare_units(self, keys: set[tuple[int, int, tuple[tuple[str, int], ...]]]) -> None:
        for key in keys:
            self._unit_cache[key] = {
                (0, "carbon.system.total"): 1.0,
                (1, "carbon.system.total"): 2.0,
            }


def _fake_ws4(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install the small WS4 surface the builder imports."""
    root = ModuleType("ws4")
    carbon = ModuleType("ws4.carbon")
    hwp = ModuleType("ws4.carbon.hwp")
    ledger = ModuleType("ws4.carbon.ledger")
    libcbm = ModuleType("ws4.carbon.libcbm")
    package = ModuleType("ws4.carbon.package")
    setattr(hwp, "load_hwp_config", lambda path: None)  # noqa: B010 - dynamic fake module
    setattr(ledger, "CarbonLedger", _FakeLedger)  # noqa: B010 - dynamic fake module
    setattr(libcbm, "cbm_defaults_reference", lambda: type("D", (), {"sha256": "defaults"})())  # noqa: B010 - dynamic fake module
    setattr(libcbm, "installed_libcbm_version", lambda: "2.10.2")  # noqa: B010 - dynamic fake module
    setattr(package, "load_carbon_package", lambda path: object())  # noqa: B010 - dynamic fake module
    setattr(package, "package_fingerprint", lambda value: "fingerprint")  # noqa: B010 - dynamic fake module
    for name, module in {
        "ws4": root,
        "ws4.carbon": carbon,
        "ws4.carbon.hwp": hwp,
        "ws4.carbon.ledger": ledger,
        "ws4.carbon.libcbm": libcbm,
        "ws4.carbon.package": package,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)


def test_build_writes_the_cache_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The builder writes an index, values, and a validated manifest."""
    _fake_ws4(monkeypatch)
    out = tmp_path / "cache"
    args = Namespace(
        dataset="dataset",
        package="package",
        hwp_config=None,
        years=1,
        offsets="0",
        treatment="CC",
        events=1,
        no_empty=False,
        workers=1,
        dtype="float64",
        limit=None,
        out=str(out),
    )
    build.build(args)
    assert (out / "index.parquet").is_file()
    assert (out / "manifest.json").is_file()
    assert (out / "values" / "empty.npy").is_file()
    assert (out / "values" / "offset_00.npy").is_file()
    assert build.parse_offsets("0,2-3") == [0, 2, 3]
    manifest = __import__("json").loads((out / "manifest.json").read_text())
    assert manifest["chain_family"]["treatment"] == "CC"
    assert manifest["chain_family"]["events"] == 1


def test_build_rejects_multiple_events(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The builder rejects a chain family outside the one-event contract."""
    _fake_ws4(monkeypatch)
    args = Namespace(
        dataset="dataset",
        package="package",
        hwp_config=None,
        years=1,
        offsets="0",
        treatment="CC",
        events=2,
        no_empty=False,
        workers=1,
        dtype="float64",
        limit=None,
        out=str(tmp_path / "cache"),
    )
    with pytest.raises(ValueError, match="one-event"):
        build.build(args)


def test_build_main_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """The console entry point documents its options."""
    with pytest.raises(SystemExit) as caught:
        build.main(["--help"])
    assert caught.value.code == 0

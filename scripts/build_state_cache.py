#!/usr/bin/env python3
"""Build an exact libcbm stand-state cache for one chain family.

The builder intentionally lives in fresh-cbm, not in the WS4 runtime. It imports
WS4's CarbonLedger so the cached rows are produced by the same exact path the
optimizer uses.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd


def parse_offsets(text: str) -> list[int]:
    """Parse ``0-49`` or ``0,1,2`` into offsets.

    Parameters
    ----------
    text : str
        Comma-separated offsets or ranges.

    Returns
    -------
    list of int
        Sorted unique offsets.
    """
    values: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            values.extend(range(int(start), int(end) + 1))
        else:
            values.append(int(part))
    if not values:
        raise ValueError("no offsets selected")
    return sorted(dict.fromkeys(values))


def build(args: argparse.Namespace) -> None:
    """Build the cache.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed builder arguments.
    """
    from ws4.carbon.hwp import load_hwp_config
    from ws4.carbon.ledger import CarbonLedger
    from ws4.carbon.libcbm import cbm_defaults_reference, installed_libcbm_version
    from ws4.carbon.package import load_carbon_package, package_fingerprint

    out = Path(args.out)
    (out / "values").mkdir(parents=True, exist_ok=True)
    package = load_carbon_package(Path(args.package))
    hwp = load_hwp_config(Path(args.hwp_config)) if args.hwp_config else None
    ledger = CarbonLedger(
        Path(args.dataset),
        package,
        years=args.years,
        hwp=hwp,
        base_workers=args.workers,
    )
    fragments = ledger.fragments
    states = (
        fragments.loc[:, ["track_id", "age"]]
        .drop_duplicates()
        .sort_values(["track_id", "age"], kind="stable")
        .reset_index(drop=True)
    )
    if args.limit is not None:
        states = states.head(args.limit).reset_index(drop=True)
    track_names = {
        int(str(row.track_id)): str(row.name) for row in ledger.tracks.itertuples(index=False)
    }
    index = pd.DataFrame(
        {
            "state_id": np.arange(len(states), dtype=np.int64),
            "track_id": states["track_id"].astype(int),
            "track_name": [track_names.get(int(value), "") for value in states["track_id"]],
            "age": states["age"].astype(int),
        }
    )
    index.to_parquet(out / "index.parquet", index=False)
    offsets = parse_offsets(args.offsets)
    started = time.perf_counter()
    accounts: tuple[str, ...] | None = None
    for offset in [-1, *offsets]:
        chain = () if offset < 0 else (("CC", int(offset)),)
        keys = {(int(row.track_id), int(row.age), chain) for row in states.itertuples(index=False)}
        step = time.perf_counter()
        ledger._prepare_units(keys)
        if accounts is None:
            first = ledger._unit_cache[next(iter(keys))]
            accounts = tuple(sorted({account for _offset, account in first}))
        values = np.zeros((len(states), args.years + 1, len(accounts)), dtype=args.dtype)
        for row, state in enumerate(states.itertuples(index=False)):
            unit = ledger._unit_cache[(int(state.track_id), int(state.age), chain)]
            for offset_index in range(args.years + 1):
                for account_index, account in enumerate(accounts):
                    values[row, offset_index, account_index] = unit.get(
                        (offset_index, account), 0.0
                    )
        name = "empty.npy" if offset < 0 else f"offset_{offset:02d}.npy"
        np.save(out / "values" / name, values, allow_pickle=False)
        ledger._unit_cache.clear()
        ledger._cache.clear()
        print(f"offset={offset:>2} states={len(states)} seconds={time.perf_counter() - step:.1f}")
    manifest = {
        "schema": "fresh-cbm-state-v1",
        "created": datetime.now(UTC).isoformat(),
        "dataset": Path(args.dataset).name,
        "package": Path(args.package).name,
        "package_fingerprint": package_fingerprint(package),
        "libcbm_version": installed_libcbm_version(),
        "cbm_defaults_sha256": cbm_defaults_reference().sha256,
        "years": args.years,
        "dtype": str(np.dtype(args.dtype)),
        "accounts": list(accounts or ()),
        "offsets": offsets,
        "empty": True,
        "states": len(states),
        "files": ["values/empty.npy", *[f"values/offset_{offset:02d}.npy" for offset in offsets]],
        "build_seconds": time.perf_counter() - started,
        "hwp_config": Path(args.hwp_config).name if args.hwp_config else None,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {out} in {time.perf_counter() - started:.1f}s")


def main() -> None:
    """Parse arguments and build the cache."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--hwp-config")
    parser.add_argument("--years", type=int, default=50)
    parser.add_argument("--offsets", default="0-49")
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--dtype", choices=["float32", "float64"], default="float64")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--out", required=True)
    build(parser.parse_args())


if __name__ == "__main__":
    main()

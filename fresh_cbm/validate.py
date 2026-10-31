"""Validate a fresh-cbm state cache against the exact WS4 carbon ledger."""

from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Sequence
from pathlib import Path

from . import StateCache


def main(argv: Sequence[str] | None = None) -> int:
    """Compare sampled cached rows with an exact ledger run.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Command-line arguments. None reads ``sys.argv``.

    Returns
    -------
    int
        Process exit status.
    """
    parser = argparse.ArgumentParser(prog="fresh-cbm-validate")
    parser.add_argument("--cache", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--hwp-config")
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--ws4-path", help="WS4 source root to add to sys.path")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    if args.ws4_path:
        sys.path.insert(0, str(args.ws4_path))
    try:
        from ws4.carbon.hwp import load_hwp_config
        from ws4.carbon.ledger import CarbonLedger
        from ws4.carbon.package import load_carbon_package
    except ImportError:  # pragma: no cover - optional installation
        print(
            "error: fresh-cbm-validate needs WS4; pass --ws4-path or set PYTHONPATH",
            file=sys.stderr,
        )
        return 1

    cache = StateCache.load(args.cache)
    ledger = CarbonLedger(
        Path(args.dataset),
        load_carbon_package(Path(args.package)),
        years=cache.years,
        hwp=load_hwp_config(Path(args.hwp_config)) if args.hwp_config else None,
        base_workers=args.workers,
    )
    rng = random.Random(args.seed)
    rows = list(range(len(cache.index)))
    rng.shuffle(rows)
    worst = 0.0
    checked = 0
    for row in rows[: args.samples]:
        state = cache.index.iloc[row]
        track = int(state.track_id)
        age = int(state.age)
        for offset in [-1, *[int(value) for value in cache.manifest["offsets"]]]:
            chain = () if offset < 0 else (("CC", offset),)
            exact = ledger._unit_accounts(track, age, chain)
            cached = cache.lookup(track, age, offset)
            for account_index, account in enumerate(cache.accounts):
                for year in range(cache.years + 1):
                    expected = float(exact.get((year, account), 0.0))
                    worst = max(worst, abs(float(cached[year, account_index]) - expected))
            checked += 1
    print(f"checked={checked} states max_abs_error={worst:.6g}")
    if worst > 1e-9:
        raise SystemExit(f"cache validation failed: max abs error {worst}")
    return 0

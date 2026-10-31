"""Repeatable cache and consumer-projection benchmarks."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from . import StateCache
from .effects import Cell, Chain, build_block_effects


@dataclass(frozen=True)
class CacheBenchmark:
    """Measured cache scale and consumer cost.

    Parameters
    ----------
    cache : str
        Cache directory.
    states : int
        Number of cached stand states.
    accounts : int
        Account count.
    offsets : int
        Chain-offset count.
    dtype : str
        Stored dtype.
    bytes : int
        Total cache size on disk.
    load_seconds : float
        Time to load and validate the cache.
    lookup_seconds : float
        Median random state lookup time.
    lookup_repeats : int
        Lookup repetitions.
    blocks : int
        Blocks in the effect projection.
    cells : int
        Target cells in the projection.
    effect_seconds : float
        Time to project the blocks onto the cells.
    """

    cache: str
    states: int
    accounts: int
    offsets: int
    dtype: str
    bytes: int
    load_seconds: float
    lookup_seconds: float
    lookup_repeats: int
    blocks: int
    cells: int
    effect_seconds: float


def _cache_bytes(root: Path) -> int:
    """Return the total size of every file under a cache root."""
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def benchmark_cache(
    cache_path: str | Path,
    fragments: pd.DataFrame,
    chains: Mapping[int, Chain],
    cells: Sequence[Cell],
    *,
    repeats: int = 100,
    seed: int = 7,
) -> CacheBenchmark:
    """Measure load, lookup, projection, and storage.

    Parameters
    ----------
    cache_path : path-like
        Cache directory.
    fragments : pandas.DataFrame
        Block/fragment rows for the projection.
    chains : mapping of int to tuple
        Current chain per block.
    cells : sequence of (int, str)
        Target cells.
    repeats : int, optional
        Random lookup repetitions. Defaults to 100.
    seed : int, optional
        Random seed. Defaults to seven.

    Returns
    -------
    CacheBenchmark
        The measured result.
    """
    if repeats < 1:
        raise ValueError("repeats must be positive")
    started = time.perf_counter()
    cache = StateCache.load(cache_path)
    load_seconds = time.perf_counter() - started
    rows = list(range(len(cache.index)))
    random.Random(seed).shuffle(rows)
    offsets = [int(value) for value in cache.manifest["offsets"]]
    samples = rows[:repeats]
    timings: list[float] = []
    for row in samples:
        state = cache.index.iloc[row]
        offset = random.Random(row).choice(offsets)
        started = time.perf_counter()
        cache.lookup(int(state.track_id), int(state.age), offset)
        timings.append(time.perf_counter() - started)
    started = time.perf_counter()
    effects = build_block_effects(cache, fragments, chains, cells)
    effect_seconds = time.perf_counter() - started
    return CacheBenchmark(
        cache=str(Path(cache_path)),
        states=len(cache.index),
        accounts=len(cache.accounts),
        offsets=len(offsets),
        dtype=str(cache.manifest["dtype"]),
        bytes=_cache_bytes(Path(cache_path)),
        load_seconds=load_seconds,
        lookup_seconds=statistics.median(timings),
        lookup_repeats=len(timings),
        blocks=len(effects.blocks),
        cells=len(effects.cells),
        effect_seconds=effect_seconds,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the cache benchmark from the command line.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Command-line arguments. None reads ``sys.argv``.

    Returns
    -------
    int
        Process exit status.
    """
    parser = argparse.ArgumentParser(prog="fresh-cbm-bench")
    parser.add_argument("--cache", required=True)
    parser.add_argument("--dataset", required=True, help="Dataset directory with fragments.parquet")
    parser.add_argument("--account", default="carbon.system.total")
    parser.add_argument("--year", type=int, default=49)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    fragments = pd.read_parquet(Path(args.dataset) / "fragments.parquet")
    blocks = sorted({int(value) for value in fragments["block_id"]})
    chains = dict.fromkeys(blocks, (("CC", args.offset),))
    result = benchmark_cache(
        args.cache,
        fragments,
        chains,
        [(args.year, args.account)],
        repeats=args.repeats,
        seed=args.seed,
    )
    payload = asdict(result)
    print(json.dumps(payload, indent=2))
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0

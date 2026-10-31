"""Project cached stand states onto block-level target cells.

The cache is aspatial and per-hectare. This module applies block/fragment area
weights and returns the base values and per-block effects for a set of target
cells. It has no WS4 dependency; a consumer can combine the carbon result with
its own simulator accounts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from . import StateCache

Cell = tuple[int, str]
Chain = tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class BlockEffects:
    """Area-weighted base values and per-block effects.

    Parameters
    ----------
    blocks : tuple of int
        Blocks in effect-row order.
    cells : tuple of (int, str)
        Target cells in column order.
    base : numpy.ndarray
        Untreated totals across every fragment.
    effects : numpy.ndarray
        Shape ``(blocks, cells)``; current-chain minus untreated per block.
    """

    blocks: tuple[int, ...]
    cells: tuple[Cell, ...]
    base: np.ndarray
    effects: np.ndarray

    def totals(self, keep: Mapping[int, bool]) -> dict[Cell, float]:
        """Return target totals for a binary keep/remove genome.

        Parameters
        ----------
        keep : mapping of int to bool
            Whether each block keeps its current chain.

        Returns
        -------
        dict of (int, str) to float
            Base plus included block effects.
        """
        values = {cell: float(self.base[column]) for column, cell in enumerate(self.cells)}
        for row, block in enumerate(self.blocks):
            if not keep.get(block, False):
                continue
            for column, cell in enumerate(self.cells):
                values[cell] += float(self.effects[row, column])
        return values


def _validate_cells(cache: StateCache, cells: Sequence[Cell]) -> None:
    """Reject cells that the cache cannot price."""
    if not cells:
        raise ValueError("at least one target cell is required")
    accounts = set(cache.accounts)
    years = cache.years
    for offset, account in cells:
        if offset < 0 or offset > years:
            raise ValueError(f"cell offset is outside the cache: {offset}")
        if account not in accounts:
            raise ValueError(f"cache has no account: {account}")


def _legacy_offset(cache: StateCache, chain: Chain) -> int:
    """Resolve a chain for a legacy manifest without a family."""
    if not chain:
        return -1
    if len(chain) != 1 or str(chain[0][0]).upper() != "CC":
        raise ValueError("legacy caches support only empty or one CC event")
    offset = int(chain[0][1])
    if offset not in {int(value) for value in cache.manifest["offsets"]}:
        raise ValueError(f"cache has no CC offset {offset}")
    return offset


def build_block_effects(
    cache: StateCache,
    fragments: pd.DataFrame,
    chains: Mapping[int, Chain],
    cells: Sequence[Cell],
) -> BlockEffects:
    """Project cached states onto block-level target cells.

    Parameters
    ----------
    cache : StateCache
        A loaded, validated cache.
    fragments : pandas.DataFrame
        Rows with ``block_id``, ``track_id``, ``age``, and ``area_ha``.
    chains : mapping of int to tuple
        Current chain per scheduled block.
    cells : sequence of (int, str)
        Target cells to project.

    Returns
    -------
    BlockEffects
        Base values and per-block current-chain effects.

    Raises
    ------
    ValueError
        When a fragment, state, chain, or cell is outside the cache contract.
    """
    required = {"block_id", "track_id", "age", "area_ha"}
    missing = required - set(fragments.columns)
    if missing:
        raise ValueError(f"fragments are missing columns: {sorted(missing)}")
    ordered_cells = tuple(cells)
    _validate_cells(cache, ordered_cells)
    row_map = {
        (int(str(row.track_id)), int(str(row.age))): int(str(row.state_id))
        for row in cache.index.itertuples(index=False)
    }
    family = cache.chain_family
    block_fragments: dict[int, list[tuple[int, int, float]]] = {}
    for row in fragments.itertuples(index=False):
        block_fragments.setdefault(int(str(row.block_id)), []).append(
            (int(str(row.track_id)), int(str(row.age)), float(str(row.area_ha)))
        )

    if family is None:
        if not bool(cache.manifest["empty"]):
            raise ValueError("block effects need a cache that stores untreated states")
    elif not family.allow_empty:
        raise ValueError("block effects need a cache that stores untreated states")
    empty = cache.array(-1)
    base = np.zeros(len(ordered_cells), dtype=np.float64)
    for track, age, area in (
        (int(str(row.track_id)), int(str(row.age)), float(str(row.area_ha)))
        for row in fragments.itertuples(index=False)
    ):
        state = row_map.get((track, age))
        if state is None:
            raise ValueError(f"state cache has no track/age {track}/{age}")
        for column, (offset, account) in enumerate(ordered_cells):
            account_index = cache.accounts.index(account)
            base[column] += area * float(empty[state, offset, account_index])

    blocks = tuple(sorted(int(block) for block in chains))
    effects = np.zeros((len(blocks), len(ordered_cells)), dtype=np.float64)
    arrays: dict[int, np.ndarray] = {-1: empty}
    for row_index, block in enumerate(blocks):
        chain = tuple(chains[block])
        offset = family.offset_for(chain) if family is not None else _legacy_offset(cache, chain)
        if offset not in arrays:
            arrays[offset] = cache.array(offset)
        if block not in block_fragments:
            raise ValueError(f"schedule block has no fragments: {block}")
        for track, age, area in block_fragments[block]:
            state = row_map.get((track, age))
            if state is None:
                raise ValueError(f"state cache has no track/age {track}/{age}")
            for column, (offset_index, account) in enumerate(ordered_cells):
                account_index = cache.accounts.index(account)
                current = float(arrays[offset][state, offset_index, account_index])
                untreated = float(empty[state, offset_index, account_index])
                effects[row_index, column] += area * (current - untreated)
    return BlockEffects(blocks=blocks, cells=ordered_cells, base=base, effects=effects)

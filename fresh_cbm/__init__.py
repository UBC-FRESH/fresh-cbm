"""Exact libcbm stand-state cache client."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StateCache:
    """A loaded exact stand-state table.

    Parameters
    ----------
    root : pathlib.Path
        Cache directory containing ``manifest.json``, ``index.parquet``, and
        ``values/``.
    manifest : dict
        Parsed manifest.
    index : pandas.DataFrame
        State index in row order.
    """

    root: Path
    manifest: dict[str, Any]
    index: pd.DataFrame

    @classmethod
    def load(cls, root: str | Path) -> StateCache:
        """Load a cache directory.

        Parameters
        ----------
        root : path-like
            Cache directory.

        Returns
        -------
        StateCache
            The loaded cache.
        """
        path = Path(root)
        manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        index = pd.read_parquet(path / "index.parquet")
        return cls(root=path, manifest=manifest, index=index)

    @property
    def accounts(self) -> tuple[str, ...]:
        """Return the cached account names."""
        return tuple(str(value) for value in self.manifest["accounts"])

    @property
    def years(self) -> int:
        """Return the stored horizon length in years."""
        return int(self.manifest["years"])

    def _row(self, track_id: int, age: int) -> int:
        """Return the index row for a track and age."""
        rows = self.index
        match = rows[
            (rows["track_id"].astype(int) == int(track_id)) & (rows["age"].astype(int) == int(age))
        ]
        if len(match) != 1:
            raise KeyError(f"state not in cache: track={track_id} age={age}")
        return int(match.iloc[0]["state_id"])

    def lookup_state(self, state_id: int, chain_offset: int = -1) -> np.ndarray:
        """Return one state's ``(years + 1, accounts)`` array.

        Parameters
        ----------
        state_id : int
            Row in ``index.parquet``.
        chain_offset : int, optional
            Single ``CC`` event offset; ``-1`` is untreated.

        Returns
        -------
        numpy.ndarray
            The cached accounts.
        """
        name = "empty.npy" if chain_offset < 0 else f"offset_{chain_offset:02d}.npy"
        values = np.load(self.root / "values" / name, mmap_mode="r")
        return np.asarray(values[int(state_id)])

    def lookup(self, track_id: int, age: int, chain_offset: int = -1) -> np.ndarray:
        """Return one state's ``(years + 1, accounts)`` array.

        Parameters
        ----------
        track_id : int
            Dataset track id.
        age : int
            Initial stand age.
        chain_offset : int, optional
            Single ``CC`` event offset; ``-1`` is untreated.

        Returns
        -------
        numpy.ndarray
            The cached accounts.
        """
        return self.lookup_state(self._row(track_id, age), chain_offset)

    def account(self, track_id: int, age: int, chain_offset: int, account: str) -> np.ndarray:
        """Return one account series for a state.

        Parameters
        ----------
        track_id : int
            Dataset track id.
        age : int
            Initial stand age.
        chain_offset : int
            Single ``CC`` event offset; ``-1`` is untreated.
        account : str
            Account name.

        Returns
        -------
        numpy.ndarray
            The account values over all stored years.
        """
        try:
            column = self.accounts.index(account)
        except ValueError as exc:
            raise KeyError(f"account not in cache: {account}") from exc
        return self.lookup(track_id, age, chain_offset)[:, column]

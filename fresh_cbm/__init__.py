"""Exact libcbm stand-state cache client."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .family import ChainFamily
from .schema import load_manifest


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
    def load(cls, root: str | Path, *, validate: bool = True) -> StateCache:
        """Load a cache directory.

        Parameters
        ----------
        root : path-like
            Cache directory.
        validate : bool, optional
            Check the index, file set, and array shapes. Defaults to True.

        Returns
        -------
        StateCache
            The loaded cache.
        """
        path = Path(root)
        manifest = load_manifest(path / "manifest.json")
        index = pd.read_parquet(path / "index.parquet")
        cache = cls(root=path, manifest=manifest, index=index)
        if validate:
            cache.validate()
        return cache

    def validate(self) -> None:
        """Check the index, file set, offsets, and array shapes.

        Raises
        ------
        ValueError
            When the cache is incomplete or inconsistent with its manifest.
        """
        required = {"state_id", "track_id", "track_name", "age"}
        missing = required - set(self.index.columns)
        if missing:
            raise ValueError(f"cache index is missing columns: {sorted(missing)}")
        states = int(self.manifest["states"])
        if len(self.index) != states:
            raise ValueError(f"cache index has {len(self.index)} rows but manifest says {states}")
        years = self.years
        accounts = len(self.accounts)
        expected = (states, years + 1, accounts)
        family = self.chain_family
        offsets = self.manifest["offsets"]
        if not isinstance(offsets, list):
            raise ValueError("manifest offsets must be a list")
        if family is not None:
            if tuple(int(value) for value in offsets) != family.offsets:
                raise ValueError("chain_family offsets do not match manifest offsets")
            if bool(self.manifest["empty"]) != family.allow_empty:
                raise ValueError("chain_family empty policy does not match manifest")
        files = self.manifest["files"]
        if not isinstance(files, list):
            raise ValueError("manifest files must be a list")
        for name in files:
            if not isinstance(name, str):
                raise ValueError("manifest file names must be strings")
            path = self.root / name
            if not path.is_file():
                raise ValueError(f"cache file is missing: {name}")
            array = np.load(path, mmap_mode="r")
            if array.shape != expected:
                raise ValueError(f"{name} has shape {array.shape}; expected {expected}")

    def verify_checksums(self, path: str | Path | None = None) -> None:
        """Verify files against a SHA256SUMS manifest.

        Parameters
        ----------
        path : path-like or None, optional
            Checksum file. Defaults to ``SHA256SUMS`` in the cache root.

        Raises
        ------
        ValueError
            When a file is missing or a digest does not match.
        """
        source = Path(path) if path is not None else self.root / "SHA256SUMS"
        if not source.is_file():
            raise ValueError(f"checksum file is missing: {source}")
        for line in source.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, name = line.split("  ", 1)
            target = self.root / name
            if not target.is_file():
                raise ValueError(f"checksum target is missing: {name}")
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual != digest:
                raise ValueError(f"checksum mismatch: {name}")

    @property
    def chain_family(self) -> ChainFamily | None:
        """Return the declared chain family, if the manifest has one.

        Returns
        -------
        ChainFamily or None
            The family record, or None for a legacy manifest without one.
        """
        raw = self.manifest.get("chain_family")
        return None if raw is None else ChainFamily.from_manifest(raw)

    @property
    def accounts(self) -> tuple[str, ...]:
        """Return the cached account names."""
        values = self.manifest["accounts"]
        if not isinstance(values, list):
            raise ValueError("manifest accounts must be a list")
        return tuple(str(value) for value in values)

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

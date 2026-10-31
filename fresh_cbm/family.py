"""Declared treatment-chain family for a state cache."""

from __future__ import annotations

from dataclasses import dataclass

Chain = tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ChainFamily:
    """The chains a cache is allowed to contain.

    The current builder supports untreated plus exactly one event from a single
    treatment. Multi-event chains are rejected explicitly rather than producing a
    cache with an ambiguous family.

    Parameters
    ----------
    treatment : str
        Treatment name, such as ``"CC"``.
    offsets : tuple of int
        Allowed event offsets.
    events : int, optional
        Events per chain. Only one is supported. Defaults to one.
    allow_empty : bool, optional
        Whether untreated rows are stored. Defaults to True.

    Raises
    ------
    ValueError
        When the treatment, offsets, event count, or empty policy is invalid.
    """

    treatment: str
    offsets: tuple[int, ...]
    events: int = 1
    allow_empty: bool = True

    def __post_init__(self) -> None:
        """Validate the family contract."""
        treatment = str(self.treatment).strip()
        if not treatment:
            raise ValueError("chain family treatment must not be empty")
        if self.events != 1:
            raise ValueError("only one-event chain families are supported")
        if not self.offsets:
            raise ValueError("chain family needs at least one offset")
        if any(offset < 0 for offset in self.offsets):
            raise ValueError("chain family offsets must be non-negative")
        if len(set(self.offsets)) != len(self.offsets):
            raise ValueError("chain family offsets must be unique")
        object.__setattr__(self, "treatment", treatment)

    def chain(self, offset: int) -> Chain:
        """Return the chain for one offset.

        Parameters
        ----------
        offset : int
            Event offset.

        Returns
        -------
        tuple of (str, int)
            The one-event chain.

        Raises
        ------
        ValueError
            When the offset is outside the family.
        """
        if int(offset) not in self.offsets:
            raise ValueError(f"offset {offset} is outside the chain family")
        return ((self.treatment, int(offset)),)

    def offset_for(self, chain: Chain) -> int:
        """Return the family offset for a chain.

        Parameters
        ----------
        chain : tuple of (str, int)
            A treatment chain.

        Returns
        -------
        int
            The event offset, or ``-1`` for untreated.

        Raises
        ------
        ValueError
            When the chain is outside the family.
        """
        if not chain:
            if not self.allow_empty:
                raise ValueError("this cache does not store untreated chains")
            return -1
        if len(chain) != 1:
            raise ValueError("only one-event chains are supported")
        treatment, offset = chain[0]
        if str(treatment).strip().upper() != self.treatment.upper():
            raise ValueError(f"treatment {treatment!r} is outside the chain family")
        if int(offset) not in self.offsets:
            raise ValueError(f"offset {offset} is outside the chain family")
        return int(offset)

    def as_manifest(self) -> dict[str, object]:
        """Return the manifest representation.

        Returns
        -------
        dict of str to object
            The JSON-compatible family record.
        """
        return {
            "treatment": self.treatment,
            "events": self.events,
            "offsets": list(self.offsets),
            "allow_empty": self.allow_empty,
        }

    @classmethod
    def from_manifest(cls, raw: object) -> ChainFamily:
        """Read a family from a manifest record.

        Parameters
        ----------
        raw : object
            Decoded ``chain_family`` value.

        Returns
        -------
        ChainFamily
            The parsed family.

        Raises
        ------
        ValueError
            When the record is malformed.
        """
        if not isinstance(raw, dict):
            raise ValueError("chain_family must be an object")
        treatment = raw.get("treatment")
        offsets = raw.get("offsets")
        events = raw.get("events", 1)
        allow_empty = raw.get("allow_empty", True)
        if not isinstance(treatment, str):
            raise ValueError("chain_family treatment must be a string")
        if not isinstance(offsets, list):
            raise ValueError("chain_family offsets must be a list")
        if not isinstance(events, int) or isinstance(events, bool):
            raise ValueError("chain_family events must be an integer")
        if not isinstance(allow_empty, bool):
            raise ValueError("chain_family allow_empty must be a boolean")
        if not all(isinstance(value, int) and not isinstance(value, bool) for value in offsets):
            raise ValueError("chain_family offsets must be integers")
        return cls(
            treatment=treatment,
            offsets=tuple(int(value) for value in offsets),
            events=events,
            allow_empty=allow_empty,
        )

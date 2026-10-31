"""Tests for the declared chain-family contract."""

from __future__ import annotations

import pytest
from fresh_cbm.family import ChainFamily


def test_family_round_trips_through_the_manifest() -> None:
    """The manifest representation reconstructs the same family."""
    family = ChainFamily("CC", (0, 1, 2))
    assert family.chain(1) == (("CC", 1),)
    assert family.offset_for((("CC", 2),)) == 2
    assert family.offset_for(()) == -1
    assert ChainFamily.from_manifest(family.as_manifest()) == family


def test_family_rejects_unsupported_chains() -> None:
    """Outside-family offsets and treatments fail clearly."""
    family = ChainFamily("CC", (0, 1))
    with pytest.raises(ValueError, match="outside"):
        family.chain(5)
    with pytest.raises(ValueError, match="treatment"):
        family.offset_for((("CT", 0),))
    with pytest.raises(ValueError, match="one-event"):
        family.offset_for((("CC", 0), ("CC", 1)))


def test_family_rejects_invalid_declarations() -> None:
    """Event counts, empty offsets, duplicates, and negative offsets are rejected."""
    with pytest.raises(ValueError, match="one-event"):
        ChainFamily("CC", (0,), events=2)
    with pytest.raises(ValueError, match="offset"):
        ChainFamily("CC", ())
    with pytest.raises(ValueError, match="unique"):
        ChainFamily("CC", (0, 0))
    with pytest.raises(ValueError, match="non-negative"):
        ChainFamily("CC", (-1,))
    with pytest.raises(ValueError, match="treatment"):
        ChainFamily(" ", (0,))


def test_family_without_empty_rejects_untreated() -> None:
    """A no-empty family rejects the untreated chain."""
    family = ChainFamily("CC", (0,), allow_empty=False)
    with pytest.raises(ValueError, match="untreated"):
        family.offset_for(())


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ([], "object"),
        ({"treatment": 1, "offsets": [0]}, "treatment"),
        ({"treatment": "CC", "offsets": "0"}, "offsets"),
        ({"treatment": "CC", "offsets": [0], "events": "1"}, "events"),
        ({"treatment": "CC", "offsets": [0], "allow_empty": "yes"}, "allow_empty"),
        ({"treatment": "CC", "offsets": ["0"]}, "integers"),
    ],
)
def test_family_rejects_malformed_manifest(raw: object, message: str) -> None:
    """Malformed family records fail clearly."""
    with pytest.raises(ValueError, match=message):
        ChainFamily.from_manifest(raw)

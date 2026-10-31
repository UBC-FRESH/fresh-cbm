"""Manifest validation for fresh-cbm state caches."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("manifest.schema.json")


def validate_manifest(raw: object) -> dict[str, object]:
    """Validate a manifest mapping against the published schema.

    Parameters
    ----------
    raw : object
        Decoded JSON value.

    Returns
    -------
    dict of str to object
        The validated manifest.

    Raises
    ------
    ValueError
        When the value is not an object or fails schema validation.
    """
    if not isinstance(raw, dict):
        raise ValueError("the cache manifest must be a JSON object")
    data = {str(key): value for key, value in raw.items()}
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid cache manifest: {detail}")
    return data


def load_manifest(path: str | Path) -> dict[str, object]:
    """Read and validate a cache manifest.

    Parameters
    ----------
    path : path-like
        Manifest path.

    Returns
    -------
    dict of str to object
        The validated manifest.
    """
    return validate_manifest(json.loads(Path(path).read_text(encoding="utf-8")))

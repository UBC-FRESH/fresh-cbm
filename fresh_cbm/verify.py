"""Offline verification of a cache release."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import StateCache


def _verify_checksum_file(root: Path) -> None:
    """Verify every entry in ``SHA256SUMS`` without loading array data."""
    source = root / "SHA256SUMS"
    if not source.is_file():
        raise ValueError(f"checksum file is missing: {source}")
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        target = root / name
        if not target.is_file():
            raise ValueError(f"checksum target is missing: {name}")
        actual = _digest(target)
        if actual != digest:
            raise ValueError(f"checksum mismatch: {name}")


def _digest(path: Path) -> str:
    """Return a file SHA-256 digest."""
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_cache(cache_path: str | Path, *, checksums: bool = True) -> dict[str, Any]:
    """Verify cache shape, optional checksums, and release metadata.

    Parameters
    ----------
    cache_path : path-like
        Cache directory.
    checksums : bool, optional
        Verify ``SHA256SUMS``. Defaults to True.

    Returns
    -------
    dict of str to object
        Verification summary.
    """
    root = Path(cache_path)
    if checksums:
        _verify_checksum_file(root)
    cache = StateCache.load(root)
    release_path = root / "release.json"
    release_checked = False
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        release_checked = True
        checks = {
            "schema": cache.manifest["schema"],
            "package_fingerprint": cache.manifest["package_fingerprint"],
            "cbm_defaults_sha256": cache.manifest["cbm_defaults_sha256"],
            "libcbm_version": cache.manifest["libcbm_version"],
            "years": cache.manifest["years"],
            "states": cache.manifest["states"],
        }
        for key, expected in checks.items():
            if key in release and release[key] != expected:
                raise ValueError(f"release.json {key} does not match manifest")
        if "total_bytes" in release and "files" in release:
            names = release["files"]
            if not isinstance(names, list):
                raise ValueError("release.json files must be a list")
            actual = sum((root / str(name)).stat().st_size for name in names)
            if int(release["total_bytes"]) != actual:
                raise ValueError("release.json total_bytes does not match cache")
    return {
        "cache": str(root),
        "states": len(cache.index),
        "accounts": len(cache.accounts),
        "offsets": len(cache.manifest["offsets"]),
        "bytes": sum(path.stat().st_size for path in root.rglob("*") if path.is_file()),
        "checksums": checksums,
        "release_checked": release_checked,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Verify a cache release from the command line.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Command-line arguments.

    Returns
    -------
    int
        Process exit status.
    """
    parser = argparse.ArgumentParser(prog="fresh-cbm-verify")
    parser.add_argument("--cache", required=True)
    parser.add_argument("--no-checksums", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        report = verify_cache(args.cache, checksums=not args.no_checksums)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(report, indent=2)
    print(text if args.json else f"verified {args.cache}\n{text}")
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    return 0

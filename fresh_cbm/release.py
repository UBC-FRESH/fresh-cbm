"""Validate cache completeness and write checksums for a release."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path


def sha256(path: Path) -> str:
    """Return a file SHA-256 digest.

    Parameters
    ----------
    path : Path
        File to hash.

    Returns
    -------
    str
        Hexadecimal digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    """Validate a cache directory and write its release checksums.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Command-line arguments. None reads ``sys.argv``.

    Returns
    -------
    int
        Process exit status.
    """
    parser = argparse.ArgumentParser(prog="fresh-cbm-package")
    parser.add_argument("--cache", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    root = Path(args.cache)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    required = ["index.parquet", "manifest.json", *manifest["files"]]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing cache files: {', '.join(missing)}")
    lines: list[str] = []
    total = 0
    for name in required:
        path = root / name
        total += path.stat().st_size
        lines.append(f"{sha256(path)}  {name}")
    output = Path(args.out) if args.out is not None else root / "SHA256SUMS"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    release = {
        "schema": manifest["schema"],
        "package_fingerprint": manifest["package_fingerprint"],
        "cbm_defaults_sha256": manifest["cbm_defaults_sha256"],
        "libcbm_version": manifest["libcbm_version"],
        "years": manifest["years"],
        "accounts": manifest["accounts"],
        "offsets": manifest["offsets"],
        "states": manifest["states"],
        "files": required,
        "total_bytes": total,
    }
    (root / "release.json").write_text(json.dumps(release, indent=2), encoding="utf-8")
    print(f"validated {len(required)} files, {total / 1e9:.2f} GB")
    print(output)
    return 0

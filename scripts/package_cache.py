#!/usr/bin/env python3
"""Backward-compatible wrapper for the ``fresh-cbm-package`` command."""

from __future__ import annotations

import sys

from fresh_cbm.release import main

if __name__ == "__main__":
    sys.exit(main())

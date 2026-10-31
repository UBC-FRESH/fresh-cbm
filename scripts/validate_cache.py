#!/usr/bin/env python3
"""Backward-compatible wrapper for the ``fresh-cbm-validate`` command."""

from __future__ import annotations

import sys

from fresh_cbm.validate import main

if __name__ == "__main__":
    sys.exit(main())

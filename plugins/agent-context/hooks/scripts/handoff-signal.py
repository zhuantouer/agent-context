#!/usr/bin/env python3
"""Compatibility entry for cached pre-0.2 Stop commands; no legacy behavior."""

import pathlib
import runpy


if __name__ == "__main__":
    runpy.run_path(str(pathlib.Path(__file__).with_name("work-signal.py")), run_name="__main__")

#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from uk1c.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

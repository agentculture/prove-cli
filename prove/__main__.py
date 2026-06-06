"""Entry point for ``python -m prove``."""

from __future__ import annotations

import sys

from prove.cli import main

if __name__ == "__main__":
    sys.exit(main())

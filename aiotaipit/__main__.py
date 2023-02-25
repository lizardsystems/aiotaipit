"""Provide a CLI for Taipit."""
from __future__ import annotations

import asyncio

from aiotaipit.cli import cli

if __name__ == "__main__":
    asyncio.run(cli())

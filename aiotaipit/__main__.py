"""Provide a CLI for Taipit."""
from __future__ import annotations

import asyncio

from aiotaipit.cli import cli


def main() -> None:
    """Run the CLI."""
    asyncio.run(cli())


if __name__ == "__main__":
    main()

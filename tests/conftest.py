"""Fixtures for aiotaipit tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses

from aiotaipit import SimpleTaipitAuth, TaipitApi
from tests.common import (
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any] | list[Any]:
    """Load a JSON fixture file by name."""
    with (FIXTURES_DIR / name).open(encoding="utf-8") as f:
        return json.load(f)


@pytest_asyncio.fixture(scope="class")
async def auth() -> SimpleTaipitAuth:
    """Create a SimpleTaipitAuth instance for integration tests."""
    async with aiohttp.ClientSession() as _session:
        _auth = SimpleTaipitAuth(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            session=_session,
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
        )
        yield _auth


@pytest_asyncio.fixture(scope="class")
async def api(auth: SimpleTaipitAuth) -> TaipitApi:
    """Create a TaipitApi instance for integration tests."""
    _api = TaipitApi(auth)
    yield _api


@pytest.fixture
def session_mock() -> aioresponses:
    """Create an aioresponses mock context."""
    with aioresponses() as mock:
        yield mock

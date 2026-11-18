"""Mocked tests for aiotaipit API module."""
from __future__ import annotations

import time

import pytest_asyncio

from aiotaipit import SimpleTaipitAuth, TaipitApi
from aiotaipit.const import DEFAULT_BASE_URL
from tests.aiohttp_mock import AiohttpClientMocker
from tests.conftest import load_fixture

API_URL = f"{DEFAULT_BASE_URL}/api"
METER_ID = 12345
USER_ID = "67890"


@pytest_asyncio.fixture
async def mock_api(aioclient_mock: AiohttpClientMocker) -> TaipitApi:
    """Create a TaipitApi with mocked auth (pre-loaded token)."""
    async with aioclient_mock.create_session() as session:
        auth = SimpleTaipitAuth(
            username="test@example.com",
            password="test",
            session=session,
            token={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            },
        )
        yield TaipitApi(auth)


class TestTaipitApiMock:
    async def test_get_meters(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/meter/list-all",
            json=load_fixture("meters_response.json"),
        )
        data = await mock_api.async_get_meters()

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == METER_ID
        assert data[0]["metername"] == "Test Meter"

    async def test_get_meter_readings(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/bmd/all?id={METER_ID}",
            json=load_fixture("meter_readings_response.json"),
        )
        data = await mock_api.async_get_meter_readings(METER_ID)

        assert data["id"] == METER_ID
        assert "readings" in data
        assert len(data["readings"]) > 0

    async def test_get_own_meters(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/meter/list-owner",
            json=load_fixture("own_meters_response.json"),
        )
        data = await mock_api.async_get_own_meters()

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == METER_ID

    async def test_get_meter_info(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/meter/get-id?id={METER_ID}",
            json=load_fixture("meter_info_response.json"),
        )
        data = await mock_api.async_get_meter_info(METER_ID)

        assert data["id"] == METER_ID
        assert data["metername"] == "Test Meter"

    async def test_get_current_user(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/user/getuser",
            json=load_fixture("current_user_response.json"),
        )
        data = await mock_api.async_get_current_user()

        assert data["id"] == 67890
        assert data["username"] == "guest@taipit.ru"

    async def test_get_user_info(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/user/getuserinfo/{USER_ID}",
            json=load_fixture("user_info_response.json"),
        )
        data = await mock_api.async_get_user_info(USER_ID)

        assert data["id"] == 67890
        assert "roles" in data

    async def test_get_warnings(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/warnings/list?action=getEntries",
            json=load_fixture("warnings_response.json"),
        )
        data = await mock_api.async_get_warnings()

        assert data["success"] is True
        assert data["data"] == []

    async def test_get_settings(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/config/settings?sections=regions%2CmeterTypes%2Ccontrollers",
            json=load_fixture("settings_response.json"),
        )
        data = await mock_api.async_get_settings()

        assert "regions" in data
        assert "meterTypes" in data
        assert "controllers" in data

    async def test_get_tariff(
        self, mock_api: TaipitApi, aioclient_mock: AiohttpClientMocker
    ) -> None:
        aioclient_mock.get(
            f"{API_URL}/meter/tariff/{METER_ID}",
            json=load_fixture("tariff_response.json"),
        )
        data = await mock_api.async_get_tariff(METER_ID)

        assert data["id"] == METER_ID
        assert "prices" in data

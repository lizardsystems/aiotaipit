"""Mocked tests for aiotaipit auth module."""
from __future__ import annotations

import re
import time
from unittest.mock import MagicMock

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses

from aiotaipit import SimpleTaipitAuth
from aiotaipit.const import DEFAULT_BASE_URL, DEFAULT_TOKEN_URL
from aiotaipit.exceptions import (
    TaipitApiError,
    TaipitAuthInvalidClient,
    TaipitAuthInvalidGrant,
    TaipitTokenAcquireFailed,
    TaipitTokenRefreshFailed,
)
from tests.conftest import load_fixture

# Token requests use query params, so we match with a regex pattern
TOKEN_URL_PATTERN = re.compile(
    re.escape(f"{DEFAULT_BASE_URL}/{DEFAULT_TOKEN_URL}") + r"(\?.*)?"
)
API_URL = f"{DEFAULT_BASE_URL}/api"
USERNAME = "testuser@example.com"
PASSWORD = "testpass"
CLIENT_ID = "test_client_id"
CLIENT_SECRET = "test_client_secret"


@pytest_asyncio.fixture
async def mock_auth() -> SimpleTaipitAuth:
    """Create a SimpleTaipitAuth instance for mocked tests."""
    async with aiohttp.ClientSession() as session:
        yield SimpleTaipitAuth(
            username=USERNAME,
            password=PASSWORD,
            session=session,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )


@pytest_asyncio.fixture
async def mock_auth_with_token() -> SimpleTaipitAuth:
    """Create a SimpleTaipitAuth with a pre-loaded valid token."""
    async with aiohttp.ClientSession() as session:
        yield SimpleTaipitAuth(
            username=USERNAME,
            password=PASSWORD,
            session=session,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token={
                "access_token": "existing_access_token",
                "refresh_token": "existing_refresh_token",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            },
        )


class TestTokenAcquire:
    async def test_new_token_success(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test acquiring a new token with password grant."""
        session_mock.get(
            TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
        )

        token = await mock_auth._async_new_token()

        assert token["access_token"] == "new_access_token"
        assert token["refresh_token"] == "new_refresh_token"
        assert token["expires_in"] == 3600
        assert "expires_at" in token

    async def test_new_token_invalid_grant(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test token acquire with wrong credentials raises InvalidGrant."""
        session_mock.get(
            TOKEN_URL_PATTERN,
            status=400,
            payload=load_fixture("token_invalid_grant.json"),
        )
        with pytest.raises(TaipitAuthInvalidGrant):
            await mock_auth._async_new_token()

    async def test_new_token_invalid_client(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test token acquire with wrong client creds raises InvalidClient."""
        session_mock.get(
            TOKEN_URL_PATTERN,
            status=400,
            payload=load_fixture("token_invalid_client.json"),
        )
        with pytest.raises(TaipitAuthInvalidClient):
            await mock_auth._async_new_token()

    async def test_new_token_http_error(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test token acquire wraps HTTP errors in TaipitTokenAcquireFailed."""
        session_mock.get(TOKEN_URL_PATTERN, status=500)
        with pytest.raises(TaipitTokenAcquireFailed):
            await mock_auth._async_new_token()

    async def test_new_token_generic_400_error(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test token acquire with unknown 400 error raises TaipitAuthError."""
        session_mock.get(
            TOKEN_URL_PATTERN,
            status=400,
            payload={"error": "unsupported_grant_type", "error_description": "Bad grant"},
        )
        with pytest.raises(TaipitTokenAcquireFailed):
            await mock_auth._async_new_token()

    async def test_new_token_invalid_response(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test token acquire raises on missing required fields."""
        session_mock.get(
            TOKEN_URL_PATTERN,
            payload={"access_token": "tok", "token_type": "bearer"},
        )
        with pytest.raises(TaipitTokenAcquireFailed):
            await mock_auth._async_new_token()


class TestTokenRefresh:
    async def test_refresh_success(
        self, mock_auth_with_token: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test refreshing a token."""
        session_mock.get(
            TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
        )

        token = await mock_auth_with_token._async_refresh_token(
            mock_auth_with_token._token
        )

        assert token["access_token"] == "new_access_token"
        assert token["refresh_token"] == "new_refresh_token"
        assert token["expires_in"] == 3600

    async def test_refresh_invalid_grant(
        self, mock_auth_with_token: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test refresh with revoked token raises InvalidGrant."""
        session_mock.get(
            TOKEN_URL_PATTERN,
            status=400,
            payload=load_fixture("token_invalid_grant.json"),
        )
        with pytest.raises(TaipitAuthInvalidGrant):
            await mock_auth_with_token._async_refresh_token(
                mock_auth_with_token._token
            )

    async def test_refresh_http_error(
        self, mock_auth_with_token: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test refresh wraps HTTP errors in TaipitTokenRefreshFailed."""
        session_mock.get(TOKEN_URL_PATTERN, status=500)
        with pytest.raises(TaipitTokenRefreshFailed):
            await mock_auth_with_token._async_refresh_token(
                mock_auth_with_token._token
            )


class TestGetAccessToken:
    async def test_valid_token_returns_cached(
        self, mock_auth_with_token: SimpleTaipitAuth
    ) -> None:
        """Test async_get_access_token returns cached token when valid."""
        token = await mock_auth_with_token.async_get_access_token()
        assert token == "existing_access_token"

    async def test_expired_token_triggers_refresh(
        self, session_mock: aioresponses
    ) -> None:
        """Test async_get_access_token refreshes expired token."""
        async with aiohttp.ClientSession() as session:
            auth = SimpleTaipitAuth(
                username=USERNAME,
                password=PASSWORD,
                session=session,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token={
                    "access_token": "old_token",
                    "refresh_token": "old_refresh",
                    "expires_in": 3600,
                    "expires_at": time.time() - 100,
                },
            )
            session_mock.get(
                TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
            )
            token = await auth.async_get_access_token()

        assert token == "new_access_token"

    async def test_no_token_triggers_acquire(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test async_get_access_token acquires new token when none exists."""
        session_mock.get(
            TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
        )
        token = await mock_auth.async_get_access_token()
        assert token == "new_access_token"


class TestTokenRestore:
    async def test_restore_valid_token(self) -> None:
        """Test constructing auth with a saved token."""
        saved_token = {
            "access_token": "restored_token",
            "refresh_token": "restored_refresh",
            "expires_in": 3600,
            "expires_at": time.time() + 3600,
        }
        async with aiohttp.ClientSession() as session:
            auth = SimpleTaipitAuth(
                username=USERNAME,
                password=PASSWORD,
                session=session,
                token=saved_token,
            )
            token = await auth.async_get_access_token()
        assert token == "restored_token"

    async def test_restore_expired_token_refreshes(
        self, session_mock: aioresponses
    ) -> None:
        """Test restored expired token triggers refresh."""
        saved_token = {
            "access_token": "expired_token",
            "refresh_token": "valid_refresh",
            "expires_in": 3600,
            "expires_at": time.time() - 100,
        }
        async with aiohttp.ClientSession() as session:
            auth = SimpleTaipitAuth(
                username=USERNAME,
                password=PASSWORD,
                session=session,
                token=saved_token,
            )
            session_mock.get(
                TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
            )
            token = await auth.async_get_access_token()
        assert token == "new_access_token"


class TestTokenUpdateCallback:
    async def test_callback_on_new_token(
        self, session_mock: aioresponses
    ) -> None:
        """Test callback is called when acquiring a new token."""
        callback = MagicMock()
        async with aiohttp.ClientSession() as session:
            auth = SimpleTaipitAuth(
                username=USERNAME,
                password=PASSWORD,
                session=session,
                token_update_callback=callback,
            )
            session_mock.get(
                TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
            )
            await auth.async_get_access_token()

        callback.assert_called_once()
        token_data = callback.call_args[0][0]
        assert token_data["access_token"] == "new_access_token"
        assert token_data["refresh_token"] == "new_refresh_token"

    async def test_callback_on_refresh(
        self, session_mock: aioresponses
    ) -> None:
        """Test callback is called when refreshing a token."""
        callback = MagicMock()
        async with aiohttp.ClientSession() as session:
            auth = SimpleTaipitAuth(
                username=USERNAME,
                password=PASSWORD,
                session=session,
                token={
                    "access_token": "old",
                    "refresh_token": "old_refresh",
                    "expires_in": 3600,
                    "expires_at": time.time() - 100,
                },
                token_update_callback=callback,
            )
            session_mock.get(
                TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
            )
            await auth.async_get_access_token()

        callback.assert_called_once()
        token_data = callback.call_args[0][0]
        assert token_data["access_token"] == "new_access_token"

    async def test_no_callback_when_not_set(
        self, mock_auth: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test no error when callback is not set."""
        session_mock.get(
            TOKEN_URL_PATTERN, payload=load_fixture("token_response.json")
        )
        token = await mock_auth.async_get_access_token()
        assert token == "new_access_token"


class TestTokenValidation:
    def test_valid_token(self) -> None:
        token = {
            "access_token": "tok",
            "refresh_token": "ref",
            "expires_in": 3600,
        }
        assert SimpleTaipitAuth._is_valid_token(token) is True

    def test_missing_access_token(self) -> None:
        token = {"refresh_token": "ref", "expires_in": 3600}
        assert SimpleTaipitAuth._is_valid_token(token) is False

    def test_missing_refresh_token(self) -> None:
        token = {"access_token": "tok", "expires_in": 3600}
        assert SimpleTaipitAuth._is_valid_token(token) is False

    def test_missing_expires_in(self) -> None:
        token = {"access_token": "tok", "refresh_token": "ref"}
        assert SimpleTaipitAuth._is_valid_token(token) is False

    def test_empty_token(self) -> None:
        assert SimpleTaipitAuth._is_valid_token({}) is False


class TestTokenExpiration:
    def test_not_expired(self) -> None:
        token = {"expires_at": time.time() + 3600}
        assert SimpleTaipitAuth._is_expired_token(token) is False

    def test_expired(self) -> None:
        token = {"expires_at": time.time() - 100}
        assert SimpleTaipitAuth._is_expired_token(token) is True

    def test_no_expires_at(self) -> None:
        token = {"access_token": "tok"}
        assert SimpleTaipitAuth._is_expired_token(token) is False


class TestRequest:
    async def test_request_success(
        self, mock_auth_with_token: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test authenticated request returns data."""
        session_mock.get(
            f"{API_URL}/test-endpoint",
            payload={"result": "ok"},
        )
        data = await mock_auth_with_token.request("GET", "api/test-endpoint")
        assert data == {"result": "ok"}

    async def test_request_http_error(
        self, mock_auth_with_token: SimpleTaipitAuth, session_mock: aioresponses
    ) -> None:
        """Test request wraps HTTP errors in TaipitApiError."""
        session_mock.get(f"{API_URL}/fail", status=500)
        with pytest.raises(TaipitApiError):
            await mock_auth_with_token.request("GET", "api/fail")

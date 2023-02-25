"""Taipit API Auth wrapper."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, cast, Optional

from aiohttp import ClientSession

from .const import (
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    DEFAULT_TOKEN_URL,
    DEFAULT_BASE_URL, TOKEN_REQUIRED_FIELDS, LOGGER
)
from .exceptions import (
    TaipitInvalidTokenResponse,
    TaipitAuthInvalidGrant,
    TaipitAuthInvalidClient,
    TaipitAuthError,
    TaipitTokenRefreshFailed,
    TaipitTokenAcquireFailed
)

CLOCK_OUT_OF_SYNC_MAX_SEC = 20


class AbstractTaipitAuth(ABC):
    """Abstract class to make authenticated requests."""
    _session: ClientSession
    _base_url: str

    def __init__(self, session: ClientSession, base_url: str = DEFAULT_BASE_URL):
        """Initialize the auth."""
        self._session = session
        self._base_url = base_url

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method: str, url: str, **kwargs) -> Any:
        """Make a request with token authorization."""
        _url = f"{self._base_url}/{url}"
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        access_token = await self.async_get_access_token()
        kwargs["headers"]["Authorization"] = f"Bearer {access_token}"

        LOGGER.debug("Request to %s with data %s", url, kwargs)

        async with self._session.request(method, _url, **kwargs) as resp:
            resp.raise_for_status()
            data = await resp.json()
            LOGGER.debug("Request finished with status=%s, headers=%s, data=%s",
                         resp.status, resp.headers, data)
        return data


class SimpleTaipitAuth(AbstractTaipitAuth):
    """Simple implementation of AbstractFlickAuth that gets a token once."""
    _username: str
    _password: str
    _client_id: str
    _client_secret: str
    _token_url: str
    _token: Optional[Dict[str, Any]] = None

    def __init__(self, username: str, password: str,
                 session: ClientSession,
                 client_id: str = DEFAULT_CLIENT_ID,
                 client_secret: str = DEFAULT_CLIENT_SECRET,
                 base_url: str = DEFAULT_BASE_URL,
                 token_url: str = DEFAULT_TOKEN_URL):
        super().__init__(session, base_url)
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url

    async def _token_request(self, data: dict) -> dict:
        """Make a token request."""
        _url = f"{self._base_url}/{self._token_url}"
        data["client_id"] = self._client_id
        data["client_secret"] = self._client_secret

        LOGGER.debug("Token request %s with data %s",
                     _url, data)

        async with self._session.post(_url, data=data) as resp:

            if resp.status == 400:
                error_info = await resp.json()
                if error_info['error'] == 'invalid_grant':
                    raise TaipitAuthInvalidGrant(error_info['error_description'])
                if error_info['error'] == 'invalid_client':
                    raise TaipitAuthInvalidClient(error_info['error_description'])
                raise TaipitAuthError

            resp.raise_for_status()

            new_token = await resp.json()

            if not self._is_valid_token(new_token):
                raise TaipitInvalidTokenResponse

            new_token["expires_in"] = int(new_token["expires_in"])
            new_token["expires_at"] = time.time() + new_token["expires_in"]

            LOGGER.debug("Token request finished %s", new_token)

            return cast(dict, new_token)

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh tokens."""
        try:
            new_token = await self._token_request(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": token["refresh_token"],
                }
            )
        except (TaipitAuthInvalidGrant, TaipitAuthInvalidClient):
            raise
        except Exception as exc:
            raise TaipitTokenRefreshFailed from exc

        return cast(dict, new_token)

    async def _async_new_token(self) -> dict:
        """Refresh tokens."""
        try:
            new_token = await self._token_request(
                {
                    "grant_type": "password",
                    "username": self._username,
                    "password": self._password
                }
            )

        except (TaipitAuthInvalidGrant, TaipitAuthInvalidClient):
            raise
        except Exception as exc:
            raise TaipitTokenAcquireFailed from exc

        return cast(dict, new_token)

    @staticmethod
    def _is_valid_token(token: dict) -> bool:
        """Check if token is valid and contains all required fields."""
        return TOKEN_REQUIRED_FIELDS <= token.keys()

    @staticmethod
    def _is_expired_token(token: dict) -> bool:
        """Check if token is not expired"""
        return (
                cast(float, token["expires_at"])
                < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC
        )

    async def async_get_access_token(self):
        """Get access token"""
        if self._token:
            if self._is_expired_token(self._token):
                self._token = await self._async_refresh_token(self._token)
        else:
            self._token = await self._async_new_token()

        return self._token["access_token"]

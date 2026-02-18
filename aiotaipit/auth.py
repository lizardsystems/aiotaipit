"""Taipit API Auth wrapper."""
from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    CLOCK_OUT_OF_SYNC_MAX_SEC,
    DEFAULT_BASE_URL,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    DEFAULT_TOKEN_URL,
    LOGGER,
    TOKEN_REQUIRED_FIELDS,
)
from .exceptions import (
    TaipitApiError,
    TaipitAuthError,
    TaipitAuthInvalidClient,
    TaipitAuthInvalidGrant,
    TaipitInvalidTokenResponse,
    TaipitTokenAcquireFailed,
    TaipitTokenRefreshFailed,
)


class AbstractTaipitAuth(ABC):
    """Abstract class to make authenticated requests."""

    def __init__(
        self,
        session: ClientSession,
        *,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        """Initialize the auth."""
        self._session = session
        self._base_url = base_url

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Make a request with token authorization."""
        _url = f"{self._base_url}/{url}"
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        access_token = await self.async_get_access_token()
        kwargs["headers"]["Authorization"] = f"Bearer {access_token}"

        LOGGER.debug("Request %s %s", method, url)

        try:
            async with self._session.request(
                method, _url, **kwargs, raise_for_status=True
            ) as resp:
                data = await resp.json()
                LOGGER.debug(
                    "Response status=%s, data=%s",
                    resp.status,
                    data,
                )
        except ClientError as err:
            raise TaipitApiError(str(err)) from err

        return data


class SimpleTaipitAuth(AbstractTaipitAuth):
    """Simple implementation of AbstractTaipitAuth that gets a token once."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        *,
        client_id: str = DEFAULT_CLIENT_ID,
        client_secret: str = DEFAULT_CLIENT_SECRET,
        base_url: str = DEFAULT_BASE_URL,
        token_url: str = DEFAULT_TOKEN_URL,
        token: dict[str, Any] | None = None,
        token_update_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        super().__init__(session, base_url=base_url)
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._token: dict[str, Any] = token if token is not None else {}
        self._lock = asyncio.Lock()
        self._token_update_callback = token_update_callback

    async def _token_request(self, data: dict[str, str]) -> dict[str, Any]:
        """Make a token request."""
        _url = f"{self._base_url}/{self._token_url}"
        data["client_id"] = self._client_id
        data["client_secret"] = self._client_secret

        LOGGER.debug("Token request grant_type=%s", data.get("grant_type"))

        try:
            async with self._session.get(_url, params=data) as resp:
                if resp.status == 400:
                    error_info = await resp.json()
                    if error_info["error"] == "invalid_grant":
                        raise TaipitAuthInvalidGrant(
                            error_info.get("error_description")
                        )
                    if error_info["error"] == "invalid_client":
                        raise TaipitAuthInvalidClient(
                            error_info.get("error_description")
                        )
                    raise TaipitAuthError(error_info.get("error_description"))
                resp.raise_for_status()

                new_token: dict[str, Any] = await resp.json()
        except (TaipitAuthError, TaipitInvalidTokenResponse):
            raise
        except ClientError as err:
            raise TaipitApiError(str(err)) from err

        if not self._is_valid_token(new_token):
            raise TaipitInvalidTokenResponse

        new_token["expires_in"] = int(new_token["expires_in"])
        new_token["expires_at"] = time.time() + new_token["expires_in"]

        LOGGER.debug(
            "Token acquired, expires_in=%s",
            new_token["expires_in"],
        )

        return new_token

    def _fire_token_update(self, token: dict[str, Any]) -> None:
        """Notify caller about token changes."""
        if self._token_update_callback is not None:
            self._token_update_callback(token)

    async def _async_refresh_token(self, token: dict[str, Any]) -> dict[str, Any]:
        """Refresh token."""
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

        return new_token

    async def _async_new_token(self) -> dict[str, Any]:
        """Get a new token."""
        try:
            new_token = await self._token_request(
                {
                    "grant_type": "password",
                    "username": self._username,
                    "password": self._password,
                }
            )
        except (TaipitAuthInvalidGrant, TaipitAuthInvalidClient):
            raise
        except Exception as exc:
            raise TaipitTokenAcquireFailed from exc

        return new_token

    @staticmethod
    def _is_valid_token(token: dict[str, Any]) -> bool:
        """Check if token is valid and contains all required fields."""
        return TOKEN_REQUIRED_FIELDS <= token.keys()

    @staticmethod
    def _is_expired_token(token: dict[str, Any]) -> bool:
        """Check if token is expired."""
        if "expires_at" in token:
            return (
                float(token["expires_at"])
                < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC
            )
        return False

    async def async_get_access_token(self) -> str:
        """Get access token."""
        async with self._lock:
            if self._is_valid_token(self._token):
                if self._is_expired_token(self._token):
                    self._token = await self._async_refresh_token(self._token)
                    self._fire_token_update(self._token)
            else:
                self._token = await self._async_new_token()
                self._fire_token_update(self._token)

        return self._token["access_token"]

"""Taipit API wrapper."""
from __future__ import annotations

from typing import Any

from .auth import AbstractTaipitAuth
from .const import (
    DEFAULT_API_URL,
    GET_ENTRIES,
    PARAM_ACTION,
    PARAM_ID,
    PARAM_SECTIONS,
    SECTIONS_ALL,
)


class TaipitApi:
    """Class to communicate with the Taipit API."""

    def __init__(
        self,
        auth: AbstractTaipitAuth,
        *,
        api_url: str = DEFAULT_API_URL,
    ) -> None:
        """Initialize the API and store the auth."""
        self._auth = auth
        self._api_url = api_url

    async def async_get(
        self, url: str, **kwargs: Any
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make async get request to api endpoint."""
        return await self._auth.request("GET", f"{self._api_url}/{url}", **kwargs)

    async def async_get_meters(self) -> list[dict[str, Any]]:
        """Get all meters and short info."""
        return await self.async_get("meter/list-all")

    async def async_get_meter_readings(self, meter_id: int) -> dict[str, Any]:
        """Get readings for meter."""
        return await self.async_get("bmd/all", params={PARAM_ID: meter_id})

    async def async_get_own_meters(self) -> list[dict[str, Any]]:
        """Get meters owned by current user."""
        return await self.async_get("meter/list-owner")

    async def async_get_meter_info(self, meter_id: int) -> dict[str, Any]:
        """Get info for meter."""
        return await self.async_get("meter/get-id", params={PARAM_ID: meter_id})

    async def async_get_current_user(self) -> dict[str, Any]:
        """Get current user info."""
        return await self.async_get("user/getuser")

    async def async_get_user_info(self, user_id: str) -> dict[str, Any]:
        """Get specified user info."""
        return await self.async_get(f"user/getuserinfo/{user_id}")

    async def async_get_warnings(self) -> dict[str, Any]:
        """List warnings."""
        return await self.async_get(
            "warnings/list", params={PARAM_ACTION: GET_ENTRIES}
        )

    async def async_get_settings(
        self, sections: tuple[str, ...] = SECTIONS_ALL
    ) -> dict[str, Any]:
        """Get settings."""
        return await self.async_get(
            "config/settings", params={PARAM_SECTIONS: ",".join(sections)}
        )

    async def async_get_tariff(self, meter_id: int) -> dict[str, Any]:
        """Get tariff for meter. Available only for meter owner."""
        return await self.async_get(f"meter/tariff/{meter_id}")

"""Taipit API wrapper."""
from __future__ import annotations

from typing import List, Any, Union

from aiohttp import hdrs

from .auth import AbstractTaipitAuth
from .const import DEFAULT_API_URL, SECTIONS_ALL, \
    PARAM_ACTION, PARAM_SECTIONS, GET_ENTRIES, PARAM_ID


class TaipitApi:
    """Class to communicate with the Taipit API."""
    _api_url: str

    def __init__(self,
                 auth: AbstractTaipitAuth,
                 *,
                 api_url: str = DEFAULT_API_URL):
        """Initialize the API and store the auth."""
        self._auth = auth
        self._api_url = api_url

    async def async_get(self, url: str, **kwargs) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """Make async get request to api endpoint"""
        return await self._auth.request(hdrs.METH_GET, f"{self._api_url}/{url}", **kwargs)

    async def async_get_meters(self) -> list[dict[str, Any]]:
        """Get all meters and short info."""
        _url = 'meter/list-all'
        return await self.async_get(_url)

    async def async_get_meter_readings(self, meter_id: int) -> dict[str, Any]:
        """Get readings for meter."""
        _url = 'bmd/all'
        params = {PARAM_ID: meter_id}
        return await self.async_get(_url, params=params)

    async def async_get_own_meters(self) -> list[dict[str, Any]]:
        """Get meters owned by current user."""
        _url = 'meter/list-owner'
        return await self.async_get(_url)

    async def async_get_meter_info(self, meter_id: int) -> dict[str, Any]:
        """Get info for meter."""
        _url = 'meter/get-id'
        params = {PARAM_ID: meter_id}
        return await self.async_get(_url, params=params)

    async def async_get_current_user(self) -> dict[str, Any]:
        """Get current user info."""
        _url = 'user/getuser'
        return await self.async_get(_url)

    async def async_get_user_info(self, user_id: str) -> dict[str, Any]:
        """Get specified user info."""
        _url = f'user/getuserinfo/{user_id}'
        return await self.async_get(_url)

    async def async_get_warnings(self) -> dict[str, Any]:
        """List warnings."""
        _params = {PARAM_ACTION: GET_ENTRIES}
        _url = f'warnings/list'
        return await self.async_get(_url, params=_params)

    async def async_get_settings(self, sections: List[str] = SECTIONS_ALL) -> dict[str, Any]:
        """Get settings"""
        _params = {PARAM_SECTIONS: ','.join(sections)}
        _url = f'config/settings'
        return await self.async_get(_url, params=_params)

    async def async_get_tariff(self, meter_id: int) -> dict[str, Any]:
        """Get tariff for meter. Available only for meter owner"""
        _url = f"meter/tariff/{meter_id}"
        return await self.async_get(_url)

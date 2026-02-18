"""Taipit API wrapper."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("aiotaipit")
except PackageNotFoundError:
    __version__ = "unknown"

from .api import TaipitApi
from .auth import AbstractTaipitAuth, SimpleTaipitAuth
from .exceptions import (
    TaipitApiError,
    TaipitAuthError,
    TaipitAuthInvalidClient,
    TaipitAuthInvalidGrant,
    TaipitError,
    TaipitInvalidTokenResponse,
    TaipitTokenAcquireFailed,
    TaipitTokenError,
    TaipitTokenRefreshFailed,
)
from .helpers import get_model_name, get_region_name

__all__ = [
    "AbstractTaipitAuth",
    "SimpleTaipitAuth",
    "TaipitApi",
    "TaipitApiError",
    "TaipitAuthError",
    "TaipitAuthInvalidClient",
    "TaipitAuthInvalidGrant",
    "TaipitError",
    "TaipitInvalidTokenResponse",
    "TaipitTokenAcquireFailed",
    "TaipitTokenError",
    "TaipitTokenRefreshFailed",
    "__version__",
    "get_model_name",
    "get_region_name",
]

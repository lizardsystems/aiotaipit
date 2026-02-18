"""Exceptions for Taipit."""
from __future__ import annotations


class TaipitError(Exception):
    """Base class for aiotaipit errors."""


class TaipitApiError(TaipitError):
    """Non-auth API/HTTP errors (e.g. server 5xx, unexpected status)."""


class TaipitAuthError(TaipitError):
    """Base class for aiotaipit auth errors."""


class TaipitAuthInvalidGrant(TaipitAuthError):
    """Invalid username and password combination."""


class TaipitAuthInvalidClient(TaipitAuthError):
    """The client credentials are invalid."""


class TaipitTokenError(TaipitError):
    """Taipit token error."""


class TaipitInvalidTokenResponse(TaipitTokenError):
    """Invalid token response."""


class TaipitTokenAcquireFailed(TaipitTokenError):
    """Failed to acquire a new token."""


class TaipitTokenRefreshFailed(TaipitTokenError):
    """Token refresh failed."""

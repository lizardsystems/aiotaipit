# aioTaipit

[![CI](https://github.com/lizardsystems/aiotaipit/actions/workflows/ci.yml/badge.svg)](https://github.com/lizardsystems/aiotaipit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/aiotaipit)](https://pypi.org/project/aiotaipit/)

Asynchronous Python API for [Taipit cloud meters](https://cloud.meters.taipit.ru).

## Installation

Use pip to install the library:

```commandline
pip install aiotaipit
```

## Usage

```python
import asyncio
from pprint import pprint

import aiohttp

from aiotaipit import SimpleTaipitAuth, TaipitApi


async def main(username: str, password: str) -> None:
    """Create the aiohttp session and run the example."""
    async with aiohttp.ClientSession() as session:
        auth = SimpleTaipitAuth(username, password, session)
        api = TaipitApi(auth)

        meters = await api.async_get_meters()

        pprint(meters)


if __name__ == "__main__":
    _username = "<YOUR_USER_NAME>"
    _password = "<YOUR_PASSWORD>"
    asyncio.run(main(_username, _password))

```
The `SimpleTaipitAuth` client also accepts custom client ID and secret (this can be found by sniffing the client).

## Exceptions

All exceptions inherit from `TaipitError`:

| Exception | Description |
|-----------|-------------|
| `TaipitApiError` | Non-auth HTTP errors (server errors, unexpected status codes) |
| `TaipitAuthError` | Base class for authentication errors |
| `TaipitAuthInvalidGrant` | Invalid username/password combination |
| `TaipitAuthInvalidClient` | Invalid OAuth client credentials |
| `TaipitTokenError` | Base class for token errors |
| `TaipitInvalidTokenResponse` | Token response missing required fields |
| `TaipitTokenAcquireFailed` | Failed to acquire a new token |
| `TaipitTokenRefreshFailed` | Failed to refresh the token |

## CLI

```commandline
# Show all meters (guest account)
python -m aiotaipit

# Show meters for a specific user
python -m aiotaipit -u user@example.com -p password

# Show meter info
python -m aiotaipit --info 12345

# Show readings
python -m aiotaipit --readings 12345

# Show settings
python -m aiotaipit --settings

# Show warnings
python -m aiotaipit --warnings
```

## Timeouts

aiotaipit does not specify any timeouts for any requests. You will need to specify them in your own code. We recommend the `timeout` from `asyncio` package:

```python
import asyncio

with asyncio.timeout(10):
    all_readings = await api.async_get_meters()
```

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.1] - 2026-11-20

### Changed

- Moved to the [ru-smarthome](https://github.com/ru-smarthome) organization on GitHub. Project URLs and author in the package metadata now point there.

## [3.1.0] - 2026-11-18

### Fixed

 - `async_get_access_token()` signs in again with the stored username and password when the server rejects the refresh token with `invalid_grant` (the refresh token expired or was revoked server-side). Previously `TaipitAuthInvalidGrant` reached the caller and required manual re-authentication. If the password is rejected as well, `TaipitAuthInvalidGrant` is raised as before.

### Changed

 - Tests mock aiohttp with an in-repo `AiohttpClientMocker` modeled on Home Assistant's `aioclient_mock` instead of `aioresponses`, which does not support aiohttp 3.14 (the version Home Assistant ships). `aioresponses` is no longer a test dependency.
 - Integration tests declare their class-scoped fixtures at module level. pytest 9.2 deprecates class-scoped fixtures defined as instance methods.

## [3.0.0] - 2026-02-18

### Added

 - `TaipitApiError` exception for non-auth HTTP failures.
 - `asyncio.Lock` in `SimpleTaipitAuth` to prevent concurrent token refresh race conditions.
 - Wrap `aiohttp.ClientError` into library exceptions (`TaipitApiError`) in `request()` and `_token_request()`.
 - Token persistence: `token` parameter in `SimpleTaipitAuth` constructor for session restore.
 - `token_update_callback` parameter - called after token acquire/refresh for token persistence.
 - `Final` type annotations on all constants in `const.py`.
 - Export all exceptions and helper functions from `__init__.py`.
 - `main()` entry point in `__main__.py` for `pyproject.toml` scripts.
 - CI workflow (`.github/workflows/ci.yml`).
 - Trusted publisher PyPI workflow (`.github/workflows/publish.yml`).
 - `[project.optional-dependencies] test` in `pyproject.toml`.
 - `[tool.pytest.ini_options] asyncio_mode = "auto"` in `pyproject.toml`.
 - Mocked unit tests with `aioresponses` (38 tests, 100% core coverage).

### Fixed

 - Mutable class-level `_token` dict shared across instances - moved to `__init__`.
 - Broken `from ._version import __version__` import in CLI.
 - `SimpleTaipitAuth()` call in CLI using positional args instead of keyword args.
 - `get_model_name()` return type: `tuple[str, str]` -> `tuple[str | None, str]`.
 - CLI always printing all meters after any command due to missing `return` statements.

### Changed

 - Sanitized debug logging: removed secrets (credentials, tokens) from log output.
 - Modernized typing: replaced `Dict`, `List`, `Tuple`, `Union`, `Optional` with builtins.
 - Removed unused `from aiohttp import hdrs` in `api.py`.
 - Removed unnecessary f-strings on static URLs.
 - Simplified `requirements_test.txt`.
 - Updated `setuptools>=64`, `aiohttp>=3`.
 - Replaced `release_to_pypi.yml` with OIDC-based `publish.yml`.
 - Removed deprecated session-scoped `event_loop` fixture from tests.
 - Removed explicit `@pytest.mark.asyncio` class decorators (automatic with `asyncio_mode = "auto"`).
 - Version fallback changed from `"0.0.0"` to `"unknown"`.
 - Regrouped `SECTION_METER_TYPES_FULL` next to other `SECTION_*` constants.

## [2.2.0] - 2024-02-26

### Updated

 - Replaced asyncio_timeout by asyncio.timeout.
 - Updated README.md.
 - Updated exception handling.


## [2.1.4] - 2023-03-08

### Fixed

 - Small fixes.

## [2.1.3] - 2023-03-05

### Added

 - Meters' model names.


## [2.1.2] - 2023-03-05

### Fixed

 - Invalid module import.


## [2.1.1] - 2023-03-04

### Added

 - Get meter model name by model id.


## [2.1.0] - 2023-02-26

### Changed

 - Token request.


## [2.0.1] - 2023-02-25

### Changed

 - Small fixes.

## [2.0.0] - 2023-02-25

First public release.

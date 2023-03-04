"""Helpers and utils."""
from __future__ import annotations

from const import REGIONS, METER_MODELS, UNKNOWN


def get_region_name(region_id: int) -> str:
    region_name = REGIONS.get(region_id, f'{UNKNOWN} <{region_id}>')
    return region_name


def get_model_name(model_id: int) -> str:
    return METER_MODELS.get(model_id, f'{UNKNOWN} <{model_id}>')

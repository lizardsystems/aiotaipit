"""Helpers and utils."""
from __future__ import annotations

from typing import Tuple

from .const import REGIONS, METER_MODELS


def get_region_name(region_id: int) -> str:
    region_name = REGIONS.get(region_id, str(region_id))
    return region_name


def get_model_name(model_id: int) -> Tuple[str, str]:
    return METER_MODELS.get(model_id, (None, str(model_id)))

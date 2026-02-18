"""Helpers and utils."""
from __future__ import annotations

from .const import METER_MODELS, REGIONS


def get_region_name(region_id: int) -> str:
    """Return region name by ID, or string ID if not found."""
    return REGIONS.get(region_id, str(region_id))


def get_model_name(model_id: int) -> tuple[str | None, str]:
    """Return (manufacturer, model_name) by model ID.

    Returns (None, str(model_id)) if the model is unknown.
    """
    return METER_MODELS.get(model_id, (None, str(model_id)))

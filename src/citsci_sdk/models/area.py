"""Area (location) model — mirrors the CitSci ``Area`` resource.

The API resource is named ``Area`` but represents a named geographic location where
observations are recorded.
"""

from __future__ import annotations

from datetime import datetime

from .base import CitSciModel, Reference


class Area(CitSciModel):
    """A named location (point) associated with a project."""

    id: int | None = None
    name: str | None = None
    # Point geometry as supplied to the API (WKT/coordinate string).
    lng_lat: str | None = None
    project: Reference | None = None
    observations_total: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

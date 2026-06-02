"""Observation model — mirrors the CitSci ``Observation`` resource."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .base import CitSciModel, Reference

if TYPE_CHECKING:  # pragma: no cover - typing only
    import ppsr_core


class Observation(CitSciModel):
    """A single observation submitted to a project/datasheet."""

    id: str | None = None
    project: Reference | None = None
    datasheet: Reference | None = None
    user: Reference | None = None
    location: Reference | None = None

    # Point geometry as supplied to the API (WKT/coordinate string), distinct from the
    # related `location` (Area) resource.
    lng_lat: str | None = None

    observed_at: datetime | None = None
    observation_ended_at: datetime | None = None
    entry_started_at: datetime | None = None
    entry_ended_at: datetime | None = None

    duration_setup: float | None = None
    duration_travel: float | None = None

    is_private: bool | None = None
    comments: str | None = None

    records: list[Reference] | None = None
    files: list[Reference] | None = None
    featured_photo: Reference | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_ppsr_core(self, **overrides: Any) -> ppsr_core.ObservationBase:
        """Convert to a PPSR Core ``ObservationBase`` (requires the ``ppsr`` extra)."""
        from ..interchange.ppsr import observation_to_ppsr_core

        return observation_to_ppsr_core(self, **overrides)

    @classmethod
    def from_ppsr_core(cls, source: ppsr_core.ObservationBase) -> Observation:
        """Build a CitSci :class:`Observation` from a PPSR Core ``ObservationBase``."""
        from ..interchange.ppsr import observation_from_ppsr_core

        return observation_from_ppsr_core(source)

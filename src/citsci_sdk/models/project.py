"""Project model — mirrors the CitSci ``Project`` resource."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .base import CitSciModel, Reference

if TYPE_CHECKING:  # pragma: no cover - typing only
    import ppsr_core


class Project(CitSciModel):
    """A CitSci project (a citizen-science effort that collects observations)."""

    id: int | None = None
    name: str | None = None
    description: str | None = None
    goals: str | None = None
    getting_started: str | None = None
    announcement: str | None = None
    announcement_date: datetime | None = None

    # Geographic centroid (free-form lat/long on the project itself).
    latitude: float | None = None
    longitude: float | None = None

    # Lifecycle: integer status code (draft/published/...). Kept as-is from the API.
    project_state: int | None = None
    is_private: bool | None = None
    is_featured: bool | None = None

    # Branding / links.
    url_field: str | None = None
    website: str | None = None
    picture: Reference | None = None
    banner_picture: Reference | None = None
    facebook_link: str | None = None
    instagram_link: str | None = None
    twitter_link: str | None = None

    # Integrations.
    is_airtable: bool | None = None
    is_zooniverse: bool | None = None
    zooniverse_id: str | None = None
    is_sci_starter: bool | None = None
    is_sci_starter_participation: bool | None = None
    sci_starter_id: str | None = None
    is_strip_image_metadata: bool | None = None

    approve_contacts: bool | None = None
    topics: list[Reference] | None = None
    tasks: list[Reference] | None = None
    user: Reference | None = None

    # Read-only aggregates / timestamps.
    measurements_total: int | None = None
    total_likes: int | None = None
    last_observation_datetime: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_ppsr_core(self, **overrides: Any) -> ppsr_core.Project:
        """Convert to a PPSR Core ``Project`` (requires the ``ppsr`` extra)."""
        from ..interchange.ppsr import project_to_ppsr_core

        return project_to_ppsr_core(self, **overrides)

    @classmethod
    def from_ppsr_core(cls, source: ppsr_core.Project) -> Project:
        """Build a CitSci :class:`Project` from a PPSR Core ``Project``."""
        from ..interchange.ppsr import project_from_ppsr_core

        return project_from_ppsr_core(source)

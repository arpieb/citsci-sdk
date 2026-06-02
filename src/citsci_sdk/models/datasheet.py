"""Datasheet models — mirror the CitSci ``Datasheet`` and ``DatasheetRecord`` resources.

A datasheet is the data-collection form/protocol for a project (analogous to a dataset's
schema); a datasheet record is a single field/question within it.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .base import CitSciModel, Reference

if TYPE_CHECKING:  # pragma: no cover - typing only
    import ppsr_core


class Datasheet(CitSciModel):
    """The form/protocol used to collect observations for a project."""

    id: int | None = None
    name: str | None = None
    instructions: str | None = None
    project: Reference | None = None

    status: int | str | None = None
    published: bool | None = None
    is_private: bool | None = None

    location_auto_assign: bool | None = None
    location_format: str | None = None
    date_format: str | None = None
    projection: str | None = None

    setup_duration_description: str | None = None
    setup_duration_format: str | None = None
    travel_duration_description: str | None = None
    travel_duration_format: str | None = None

    records: list[Reference] | None = None
    zooniverse_history: Reference | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_ppsr_core(self, **overrides: Any) -> ppsr_core.DatasetMetadata:
        """Convert to a PPSR Core ``DatasetMetadata`` (requires the ``ppsr`` extra)."""
        from ..interchange.ppsr import datasheet_to_ppsr_core

        return datasheet_to_ppsr_core(self, **overrides)

    @classmethod
    def from_ppsr_core(cls, source: ppsr_core.DatasetMetadata) -> Datasheet:
        """Build a CitSci :class:`Datasheet` from a PPSR Core ``DatasetMetadata``."""
        from ..interchange.ppsr import datasheet_from_ppsr_core

        return datasheet_from_ppsr_core(source)


class DatasheetRecord(CitSciModel):
    """A single field/question within a datasheet."""

    id: int | None = None
    datasheet: Reference | None = None
    records: list[Reference] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

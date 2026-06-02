"""The ``areas`` resource namespace (named locations)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ..models.area import Area
from .base import BaseResource


class AreasResource(BaseResource[Area]):
    model = Area
    collection_path = "/areas"

    def get(self, area_id: int | str) -> Area:
        return self._get(area_id)

    def for_project(self, project_id: int | str, **kwargs: Any) -> Iterator[Area]:
        """Iterate locations for a project (``GET /projects/{id}/locations``)."""
        return self._iterate(f"/projects/{project_id}/locations", **kwargs)

    def create(self, data: Area | dict[str, Any]) -> Area:
        return self._create(data)

    def update(self, area_id: int | str, data: Area | dict[str, Any]) -> Area:
        return self._update(area_id, data)

    def delete(self, area_id: int | str) -> None:
        self._delete(area_id)

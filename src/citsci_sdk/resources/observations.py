"""The ``observations`` resource namespace."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ..models.observation import Observation
from .base import BaseResource


class ObservationsResource(BaseResource[Observation]):
    model = Observation
    collection_path = "/observations"

    def get(self, observation_id: int | str) -> Observation:
        return self._get(observation_id)

    def list(
        self, *, page: int = 1, items_per_page: int | None = None, **filters: Any
    ) -> list[Observation]:
        """Retrieve one page of public observations.

        Filters map directly to API query params, e.g. ``project_filter`` is not a thing —
        pass them with their API names via ``**filters`` (e.g. ``**{"project.id": 42})``).
        """
        return self._list_page(page=page, items_per_page=items_per_page, params=filters or None)

    def iterate(
        self, *, items_per_page: int | None = None, max_items: int | None = None, **filters: Any
    ) -> Iterator[Observation]:
        return self._iterate(
            items_per_page=items_per_page, max_items=max_items, params=filters or None
        )

    def for_project(self, project_id: int | str, **kwargs: Any) -> Iterator[Observation]:
        """Iterate observations for a project (``GET /projects/{id}/observations``)."""
        return self._iterate(f"/projects/{project_id}/observations", **kwargs)

    def for_user(self, user_id: int | str, **kwargs: Any) -> Iterator[Observation]:
        """Iterate observations for a user (``GET /users/{id}/observations``)."""
        return self._iterate(f"/users/{user_id}/observations", **kwargs)

    def for_datasheet(self, datasheet_id: int | str, **kwargs: Any) -> Iterator[Observation]:
        """Iterate observations for a datasheet (``GET /datasheets/{id}/observations``)."""
        return self._iterate(f"/datasheets/{datasheet_id}/observations", **kwargs)

    def for_area(self, area_id: int | str, **kwargs: Any) -> Iterator[Observation]:
        """Iterate observations at a location (``GET /areas/{id}/observations``)."""
        return self._iterate(f"/areas/{area_id}/observations", **kwargs)

    def create(self, data: Observation | dict[str, Any]) -> Observation:
        return self._create(data)

    def update(self, observation_id: int | str, data: Observation | dict[str, Any]) -> Observation:
        return self._update(observation_id, data)

    def patch(self, observation_id: int | str, data: Observation | dict[str, Any]) -> Observation:
        return self._patch(observation_id, data)

    def delete(self, observation_id: int | str) -> None:
        self._delete(observation_id)

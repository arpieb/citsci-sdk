"""The ``projects`` resource namespace."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ..models.project import Project
from .base import BaseResource


class ProjectsResource(BaseResource[Project]):
    model = Project
    collection_path = "/projects"

    def get(self, project_id: int | str) -> Project:
        """Retrieve a single project by id."""
        return self._get(project_id)

    def list(
        self, *, page: int = 1, items_per_page: int | None = None, **filters: Any
    ) -> list[Project]:
        """Retrieve one page of published projects."""
        return self._list_page(page=page, items_per_page=items_per_page, params=filters or None)

    def iterate(
        self, *, items_per_page: int | None = None, max_items: int | None = None, **filters: Any
    ) -> Iterator[Project]:
        """Iterate over all published projects, transparently paging."""
        return self._iterate(
            items_per_page=items_per_page, max_items=max_items, params=filters or None
        )

    def for_user(self, user_id: int | str, **kwargs: Any) -> Iterator[Project]:
        """Iterate over projects created by a user (``GET /users/{id}/projects``)."""
        return self._iterate(f"/users/{user_id}/projects", **kwargs)

    def create(self, data: Project | dict[str, Any]) -> Project:
        return self._create(data)

    def update(self, project_id: int | str, data: Project | dict[str, Any]) -> Project:
        """Replace a project (``PUT``)."""
        return self._update(project_id, data)

    def patch(self, project_id: int | str, data: Project | dict[str, Any]) -> Project:
        """Partially update a project (``PATCH``)."""
        return self._patch(project_id, data)

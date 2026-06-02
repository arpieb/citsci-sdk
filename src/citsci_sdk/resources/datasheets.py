"""The ``datasheets`` resource namespace (datasheets + their records)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ..models.datasheet import Datasheet, DatasheetRecord
from ..pagination import iterate_pages
from .base import BaseResource


class DatasheetsResource(BaseResource[Datasheet]):
    model = Datasheet
    collection_path = "/datasheets"

    def get(self, datasheet_id: int | str) -> Datasheet:
        return self._get(datasheet_id)

    def list(
        self, *, page: int = 1, items_per_page: int | None = None, **filters: Any
    ) -> list[Datasheet]:
        return self._list_page(page=page, items_per_page=items_per_page, params=filters or None)

    def iterate(
        self, *, items_per_page: int | None = None, max_items: int | None = None, **filters: Any
    ) -> Iterator[Datasheet]:
        return self._iterate(
            items_per_page=items_per_page, max_items=max_items, params=filters or None
        )

    def for_project(self, project_id: int | str, **kwargs: Any) -> Iterator[Datasheet]:
        """Iterate datasheets for a project (``GET /projects/{id}/datasheets``)."""
        return self._iterate(f"/projects/{project_id}/datasheets", **kwargs)

    def records(self, datasheet_id: int | str, **kwargs: Any) -> Iterator[DatasheetRecord]:
        """Iterate the records of a datasheet (``GET /datasheets/{id}/records``)."""

        def fetch(page: int, per_page: int) -> list[Any]:
            return (
                self._t.get(
                    f"/datasheets/{datasheet_id}/records",
                    params={"page": page, "itemsPerPage": per_page},
                )
                or []
            )

        return iterate_pages(fetch, parse=DatasheetRecord.model_validate, **kwargs)

    def create(self, data: Datasheet | dict[str, Any]) -> Datasheet:
        return self._create(data)

    def update(self, datasheet_id: int | str, data: Datasheet | dict[str, Any]) -> Datasheet:
        return self._update(datasheet_id, data)

    def patch(self, datasheet_id: int | str, data: Datasheet | dict[str, Any]) -> Datasheet:
        return self._patch(datasheet_id, data)

    def delete(self, datasheet_id: int | str) -> None:
        self._delete(datasheet_id)

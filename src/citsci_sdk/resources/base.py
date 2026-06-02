"""Shared CRUD behaviour for resource namespaces."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Generic, TypeVar

from ..http import Transport
from ..models.base import CitSciModel
from ..pagination import iterate_pages

M = TypeVar("M", bound=CitSciModel)


class BaseResource(Generic[M]):
    """Generic CRUD + pagination over a single API collection.

    Subclasses set :attr:`model` and :attr:`collection_path`. Not every endpoint supports
    every verb; subclasses only expose the ones the API actually offers.
    """

    model: type[M]
    collection_path: str

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    # -- helpers ------------------------------------------------------------------

    def _item_path(self, id: Any) -> str:
        return f"{self.collection_path}/{id}"

    def _parse(self, raw: Any) -> M:
        return self.model.model_validate(raw)

    def _payload(self, data: M | dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, CitSciModel):
            return data.to_api_payload()
        return data

    # -- reads --------------------------------------------------------------------

    def _get(self, id: Any) -> M:
        return self._parse(self._t.get(self._item_path(id)))

    def _list_page(
        self,
        path: str | None = None,
        *,
        page: int = 1,
        items_per_page: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[M]:
        query = dict(params or {})
        query["page"] = page
        if items_per_page is not None:
            query["itemsPerPage"] = items_per_page
        raw = self._t.get(path or self.collection_path, params=query)
        return [self._parse(item) for item in (raw or [])]

    def _iterate(
        self,
        path: str | None = None,
        *,
        items_per_page: int | None = None,
        max_items: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Iterator[M]:
        target = path or self.collection_path

        def fetch(page: int, per_page: int) -> list[Any]:
            query = dict(params or {})
            query["page"] = page
            query["itemsPerPage"] = per_page
            return self._t.get(target, params=query) or []

        return iterate_pages(
            fetch, items_per_page=items_per_page, parse=self._parse, max_items=max_items
        )

    # -- writes -------------------------------------------------------------------

    def _create(self, data: M | dict[str, Any]) -> M:
        return self._parse(self._t.post(self.collection_path, json=self._payload(data)))

    def _update(self, id: Any, data: M | dict[str, Any]) -> M:
        return self._parse(self._t.put(self._item_path(id), json=self._payload(data)))

    def _patch(self, id: Any, data: M | dict[str, Any]) -> M:
        return self._parse(self._t.patch(self._item_path(id), json=self._payload(data)))

    def _delete(self, id: Any) -> None:
        self._t.delete(self._item_path(id))

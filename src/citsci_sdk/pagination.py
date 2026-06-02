"""Pagination helpers for CitSci collection endpoints.

CitSci paginates collections with the Hydra query params ``page`` (1-based) and
``itemsPerPage`` (capped at :data:`~citsci_sdk.config.MAX_ITEMS_PER_PAGE`). In the plain
``application/json`` representation the SDK uses, a collection response is a *bare JSON
array* with no envelope — there is no total count or "next page" link. So we walk pages
until the API returns a page shorter than ``itemsPerPage`` (or an empty page).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, TypeVar

from .config import MAX_ITEMS_PER_PAGE

T = TypeVar("T")

# A callable that fetches one page given (page_number, items_per_page) and returns the
# raw list of items for that page.
PageFetcher = Callable[[int, int], list[Any]]


def clamp_items_per_page(items_per_page: int | None) -> int:
    """Clamp a requested page size to the server's allowed range (1..MAX)."""
    if items_per_page is None:
        return MAX_ITEMS_PER_PAGE
    return max(1, min(items_per_page, MAX_ITEMS_PER_PAGE))


def iterate_pages(
    fetch: PageFetcher,
    *,
    items_per_page: int | None = None,
    start_page: int = 1,
    parse: Callable[[Any], T] | None = None,
    max_items: int | None = None,
) -> Iterator[T]:
    """Yield items across pages until the collection is exhausted.

    Args:
        fetch: Returns the list of raw items for ``(page, items_per_page)``.
        items_per_page: Requested page size; clamped to the server maximum.
        start_page: First page number (1-based).
        parse: Optional transform applied to each raw item (e.g. model validation).
        max_items: Optional hard cap on the number of items yielded.
    """
    per_page = clamp_items_per_page(items_per_page)
    page = start_page
    yielded = 0
    while True:
        items = fetch(page, per_page)
        if not items:
            return
        for raw in items:
            yield parse(raw) if parse else raw
            yielded += 1
            if max_items is not None and yielded >= max_items:
                return
        # A short page means we've reached the end — no need for another round trip.
        if len(items) < per_page:
            return
        page += 1

"""Collection pagination: walk pages until a short/empty page; clamp page size."""

import httpx
import respx

from citsci_sdk import CitSciClient
from citsci_sdk.pagination import clamp_items_per_page


def _page(n, size):
    """A page of `size` observations with sequential ids starting at (n-1)*size+1."""
    start = (n - 1) * size + 1
    return [{"id": str(i), "lngLat": None} for i in range(start, start + size)]


def test_clamp_items_per_page():
    assert clamp_items_per_page(None) == 30
    assert clamp_items_per_page(5) == 5
    assert clamp_items_per_page(1000) == 30  # server cap
    assert clamp_items_per_page(0) == 1


@respx.mock
def test_iterate_walks_pages_until_short_page():
    # Two full pages of 2, then a final short page of 1 → iteration stops (no 4th call).
    respx.get("https://api.citsci.org/observations").mock(
        side_effect=[
            httpx.Response(200, json=_page(1, 2)),
            httpx.Response(200, json=_page(2, 2)),
            httpx.Response(200, json=[{"id": "5", "lngLat": None}]),
        ]
    )

    with CitSciClient(token="t") as client:
        ids = [o.id for o in client.observations.iterate(items_per_page=2)]

    assert ids == ["1", "2", "3", "4", "5"]


@respx.mock
def test_iterate_respects_max_items():
    route = respx.get("https://api.citsci.org/observations").mock(
        side_effect=[httpx.Response(200, json=_page(n, 2)) for n in range(1, 11)]
    )

    with CitSciClient(token="t") as client:
        ids = [o.id for o in client.observations.iterate(items_per_page=2, max_items=3)]

    assert ids == ["1", "2", "3"]
    # Stopped after the second page (max_items reached mid-page), not all 10.
    assert route.call_count == 2


@respx.mock
def test_iterate_stops_on_empty_first_page():
    respx.get("https://api.citsci.org/observations").mock(return_value=httpx.Response(200, json=[]))
    with CitSciClient(token="t") as client:
        assert list(client.observations.iterate(items_per_page=5)) == []

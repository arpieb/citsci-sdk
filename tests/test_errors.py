"""Mapping of HTTP error responses to typed exceptions."""

import httpx
import pytest
import respx

from citsci_sdk import (
    CitSciClient,
    NotFoundError,
    ServerError,
    ValidationError,
)

BASE = "https://api.citsci.org"


@respx.mock
def test_404_maps_to_not_found():
    respx.get(f"{BASE}/projects/999").mock(
        return_value=httpx.Response(404, json={"detail": "Not Found", "title": "An error occurred"})
    )
    with CitSciClient(token="t") as client:
        with pytest.raises(NotFoundError) as exc:
            client.projects.get(999)
    assert exc.value.status_code == 404
    assert "Not Found" in str(exc.value)


@respx.mock
def test_422_maps_to_validation_error_with_violations():
    violations = [{"propertyPath": "name", "message": "This value should not be blank."}]
    respx.post(f"{BASE}/projects").mock(
        return_value=httpx.Response(422, json={"detail": "name: blank", "violations": violations})
    )
    with CitSciClient(token="t") as client:
        with pytest.raises(ValidationError) as exc:
            client.projects.create({"name": ""})
    assert exc.value.violations == violations
    assert exc.value.status_code == 422


@respx.mock
def test_5xx_maps_to_server_error():
    respx.get(f"{BASE}/projects/1").mock(return_value=httpx.Response(503, text="upstream down"))
    with CitSciClient(token="t") as client:
        with pytest.raises(ServerError) as exc:
            client.projects.get(1)
    assert exc.value.status_code == 503

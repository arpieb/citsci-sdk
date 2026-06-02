"""Model (de)serialization and request-body shaping."""

from datetime import datetime

import httpx
import respx

from citsci_sdk import CitSciClient, Observation, Project

BASE = "https://api.citsci.org"


def test_project_parses_camelcase_and_round_trips():
    raw = {
        "id": "a4ea86cb-d85b-4c56-be3e-5e23c8ed66b9",
        "name": "Backyard Birds",
        "urlField": "backyard-birds",
        "isZooniverse": True,
        "createdAt": "2024-01-02T03:04:05+00:00",
        "facebookLink": "https://fb.com/x",
    }
    project = Project.model_validate(raw)

    # camelCase wire names become snake_case attributes.
    assert project.url_field == "backyard-birds"
    assert project.is_zooniverse is True
    assert project.created_at == datetime.fromisoformat("2024-01-02T03:04:05+00:00")

    # ...and round-trip back to the API's camelCase names.
    payload = project.to_api_payload()
    assert payload["urlField"] == "backyard-birds"
    assert payload["isZooniverse"] is True
    assert "isPrivate" not in payload  # exclude_none drops unset fields


def test_extra_fields_are_preserved():
    obs = Observation.model_validate({"id": "1", "someFutureField": "kept"})
    assert obs.model_dump(by_alias=True)["someFutureField"] == "kept"


@respx.mock
def test_create_sends_camelcase_json_body():
    route = respx.post(f"{BASE}/observations").mock(
        return_value=httpx.Response(201, json={"id": "99"})
    )
    with CitSciClient(token="t") as client:
        created = client.observations.create(
            Observation(lng_lat="POINT(-105 40)", duration_setup=1.5)
        )

    import json

    sent = json.loads(route.calls.last.request.content)
    assert sent == {"lngLat": "POINT(-105 40)", "durationSetup": 1.5}
    assert route.calls.last.request.headers["Content-Type"] == "application/json"
    assert created.id == "99"


@respx.mock
def test_patch_uses_merge_patch_content_type():
    route = respx.patch(f"{BASE}/observations/5").mock(
        return_value=httpx.Response(200, json={"id": "5", "isPrivate": True})
    )
    with CitSciClient(token="t") as client:
        client.observations.patch(5, {"isPrivate": True})

    assert route.calls.last.request.headers["Content-Type"] == "application/merge-patch+json"

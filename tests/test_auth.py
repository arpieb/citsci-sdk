"""Authentication flow: login on demand, refresh + retry on 401, re-login fallback."""

import httpx
import respx

from citsci_sdk import CitSciClient

BASE = "https://api.citsci.org"


@respx.mock
def test_logs_in_on_first_request_and_sends_bearer_token():
    login = respx.post(f"{BASE}/login").mock(
        return_value=httpx.Response(201, json={"token": "jwt-1", "refresh_token": "ref-1"})
    )
    projects = respx.get(f"{BASE}/projects/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Birds"})
    )

    with CitSciClient(email="me@example.com", password="pw") as client:
        project = client.projects.get(1)

    assert login.called
    assert project.name == "Birds"
    # The login body carried the credentials, and the follow-up request was authorized.
    import json

    assert json.loads(login.calls.last.request.content) == {
        "email": "me@example.com",
        "password": "pw",
    }
    assert projects.calls.last.request.headers["Authorization"] == "Bearer jwt-1"


@respx.mock
def test_refreshes_and_retries_once_on_401():
    get_project = respx.get(f"{BASE}/projects/1").mock(
        side_effect=[
            httpx.Response(401, json={"detail": "Expired JWT"}),
            httpx.Response(200, json={"id": 1, "name": "Birds"}),
        ]
    )
    refresh = respx.post(f"{BASE}/token/refresh").mock(
        return_value=httpx.Response(200, json={"token": "jwt-2", "refresh_token": "ref-2"})
    )

    with CitSciClient(token="jwt-old", refresh_token="ref-1") as client:
        project = client.projects.get(1)

    assert refresh.called
    assert project.id == 1
    assert get_project.call_count == 2
    # The retry used the freshly minted token.
    assert get_project.calls[-1].request.headers["Authorization"] == "Bearer jwt-2"


@respx.mock
def test_falls_back_to_login_when_refresh_rejected():
    respx.get(f"{BASE}/projects/1").mock(
        side_effect=[
            httpx.Response(401, json={"detail": "Expired JWT"}),
            httpx.Response(200, json={"id": 1, "name": "Birds"}),
        ]
    )
    refresh = respx.post(f"{BASE}/token/refresh").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid refresh token"})
    )
    login = respx.post(f"{BASE}/login").mock(
        return_value=httpx.Response(201, json={"token": "jwt-3", "refresh_token": "ref-3"})
    )

    with CitSciClient(
        email="me@example.com", password="pw", token="jwt-old", refresh_token="bad"
    ) as client:
        project = client.projects.get(1)

    assert refresh.called
    assert login.called
    assert project.id == 1

"""Low-level HTTP transport: auth orchestration, serialization, error mapping.

This wraps a single :class:`httpx.Client`. Resource classes never touch httpx directly;
they call :meth:`Transport.request` and friends, which:

* attach the ``Authorization`` header (logging in on demand),
* serialize JSON request bodies with the right ``Content-Type``,
* transparently refresh / re-login once on a ``401`` and retry,
* map any non-2xx response to a typed :class:`~citsci_sdk.errors.CitSciAPIError`.
"""

from __future__ import annotations

import json as jsonlib
from typing import Any

import httpx

from .auth import LOGIN_PATH, REFRESH_PATH, TokenAuth
from .config import ClientConfig
from .errors import AuthenticationError, CitSciConfigError, error_from_response

JSON_CONTENT_TYPE = "application/json"
MERGE_PATCH_CONTENT_TYPE = "application/merge-patch+json"


class Transport:
    def __init__(
        self,
        auth: TokenAuth,
        config: ClientConfig | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self.auth = auth
        self.config = config or ClientConfig()
        self._client = client or httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={"User-Agent": self.config.user_agent},
        )

    # -- public API ---------------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        content_type: str = JSON_CONTENT_TYPE,
        authenticated: bool = True,
    ) -> Any:
        """Send a request and return the decoded JSON body (or ``None`` for 204)."""
        if authenticated:
            self._ensure_token()

        response = self._send(
            method,
            path,
            params=params,
            json=json,
            content_type=content_type,
            authenticated=authenticated,
        )

        if response.status_code == 401 and authenticated:
            # Token expired or rejected: refresh (or re-login) and retry exactly once.
            self._reauthenticate()
            response = self._send(
                method,
                path,
                params=params,
                json=json,
                content_type=content_type,
                authenticated=True,
            )

        if response.status_code >= 400:
            raise error_from_response(response.status_code, _safe_json(response))
        return _safe_json(response)

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Any:
        kwargs.setdefault("content_type", MERGE_PATCH_CONTENT_TYPE)
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self._client.close()

    # -- auth orchestration -------------------------------------------------------

    def _ensure_token(self) -> None:
        if not self.auth.has_token:
            self._login()

    def _reauthenticate(self) -> None:
        self.auth.clear_token()
        if self.auth.can_refresh:
            try:
                self._refresh()
                return
            except AuthenticationError:
                # Refresh token invalid/expired — fall back to a full login.
                self.auth.clear_token()
        self._login()

    def _login(self) -> None:
        body = self._send("POST", LOGIN_PATH, json=self.auth.login_payload(), authenticated=False)
        self._store_tokens(body, context="login")

    def _refresh(self) -> None:
        body = self._send(
            "POST", REFRESH_PATH, json=self.auth.refresh_payload(), authenticated=False
        )
        self._store_tokens(body, context="token refresh")

    def _store_tokens(self, response: httpx.Response, context: str) -> None:
        if response.status_code >= 400:
            raise error_from_response(response.status_code, _safe_json(response))
        data = _safe_json(response)
        if not isinstance(data, dict) or not data.get("token"):
            raise CitSciConfigError(f"Unexpected {context} response: no token returned.")
        self.auth.set_tokens(data["token"], data.get("refresh_token"))

    # -- raw send -----------------------------------------------------------------

    def _send(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        content_type: str = JSON_CONTENT_TYPE,
        authenticated: bool = True,
    ) -> httpx.Response:
        headers = {"Accept": JSON_CONTENT_TYPE}
        content: bytes | None = None
        if json is not None:
            content = jsonlib.dumps(json).encode("utf-8")
            headers["Content-Type"] = content_type
        if authenticated:
            token = self.auth.token
            if token:
                headers["Authorization"] = self.config.authorization(token)
        return self._client.request(
            method, path, params=_clean_params(params), content=content, headers=headers
        )


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values so optional filters don't show up as empty query params."""
    if not params:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _safe_json(response: httpx.Response) -> Any:
    if response.status_code == 204 or not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return None

"""The top-level :class:`CitSciClient`."""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx

from .auth import TokenAuth
from .config import ClientConfig
from .http import Transport
from .resources import (
    AreasResource,
    DatasheetsResource,
    ObservationsResource,
    ProjectsResource,
)


class CitSciClient:
    """Synchronous client for the CitSci API (https://api.citsci.org).

    Authenticate with either email + password (the client logs in and refreshes tokens on
    demand) or an existing JWT::

        with CitSciClient(email="me@example.com", password="…") as client:
            for obs in client.observations.iterate(items_per_page=5, max_items=20):
                print(obs.observed_at)

    Resource namespaces: :attr:`projects`, :attr:`observations`, :attr:`datasheets`,
    :attr:`areas`.
    """

    def __init__(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        token: str | None = None,
        refresh_token: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        config: ClientConfig | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        cfg = config or ClientConfig()
        if base_url is not None:
            cfg.base_url = base_url.rstrip("/")
        if timeout is not None:
            cfg.timeout = timeout

        self._auth = TokenAuth(
            email=email, password=password, token=token, refresh_token=refresh_token
        )
        self._transport = Transport(self._auth, cfg, client=http_client)

        self.projects = ProjectsResource(self._transport)
        self.observations = ObservationsResource(self._transport)
        self.datasheets = DatasheetsResource(self._transport)
        self.areas = AreasResource(self._transport)

    @property
    def token(self) -> str | None:
        """The current access token, if one has been obtained."""
        return self._auth.token

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> CitSciClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"CitSciClient(base_url={self._transport.config.base_url!r})"

    # Escape hatch for endpoints not yet wrapped by a resource namespace.
    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make a raw authenticated request and return the decoded JSON body."""
        return self._transport.request(method, path, **kwargs)

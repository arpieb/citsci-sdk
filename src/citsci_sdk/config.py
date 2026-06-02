"""Client configuration."""

from __future__ import annotations

from dataclasses import dataclass

from . import __version__

DEFAULT_BASE_URL = "https://api.citsci.org"
DEFAULT_TIMEOUT = 30.0
DEFAULT_USER_AGENT = f"citsci-sdk/{__version__} (+https://api.citsci.org)"

# CitSci collections are paginated via Hydra query params. `itemsPerPage` is capped
# server-side at 30 for the resources this SDK covers.
MAX_ITEMS_PER_PAGE = 30


@dataclass(slots=True)
class ClientConfig:
    """Static configuration for a :class:`~citsci_sdk.client.CitSciClient`."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    user_agent: str = DEFAULT_USER_AGENT
    # The CitSci API advertises an apiKey scheme on the `Authorization` header. It is
    # backed by LexikJWT, which expects a `Bearer ` prefix. Exposed for the rare server
    # that wants the bare token instead (set to "").
    auth_header_scheme: str = "Bearer"

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def authorization(self, token: str) -> str:
        """Build the ``Authorization`` header value for *token*."""
        scheme = self.auth_header_scheme.strip()
        return f"{scheme} {token}" if scheme else token

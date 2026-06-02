"""Credential and token state for the CitSci API.

The API authenticates with a JWT obtained from ``POST /login`` (email + password). The
JWT is short-lived; a longer-lived ``refresh_token`` can mint a new one via
``POST /token/refresh``. When the refresh token is also rejected, the client must
re-authenticate with email and password.

This module only holds the auth *state* and decides what to do next. The actual HTTP
calls to ``/login`` and ``/token/refresh`` live in :mod:`citsci_sdk.http`, which owns the
network transport.
"""

from __future__ import annotations

from .errors import CitSciConfigError

LOGIN_PATH = "/login"
REFRESH_PATH = "/token/refresh"


class TokenAuth:
    """Holds CitSci credentials and the current JWT / refresh-token pair."""

    def __init__(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        if not (email and password) and not token:
            raise CitSciConfigError(
                "Provide either email + password, or an existing token, to authenticate."
            )
        self.email = email
        self.password = password
        self._token = token
        self._refresh_token = refresh_token

    @property
    def token(self) -> str | None:
        return self._token

    @property
    def refresh_token(self) -> str | None:
        return self._refresh_token

    @property
    def has_token(self) -> bool:
        return bool(self._token)

    @property
    def can_login(self) -> bool:
        """Whether email + password are available for a fresh ``/login``."""
        return bool(self.email and self.password)

    @property
    def can_refresh(self) -> bool:
        return bool(self._refresh_token)

    def set_tokens(self, token: str, refresh_token: str | None = None) -> None:
        self._token = token
        if refresh_token is not None:
            self._refresh_token = refresh_token

    def clear_token(self) -> None:
        """Forget the current access token (e.g. after a 401)."""
        self._token = None

    def login_payload(self) -> dict[str, str]:
        if not self.can_login:
            raise CitSciConfigError(
                "Cannot log in: this client was created with a token but no email/password, "
                "and the token was rejected. Recreate the client with credentials."
            )
        return {"email": self.email, "password": self.password}  # type: ignore[dict-item]

    def refresh_payload(self) -> dict[str, str]:
        if not self.can_refresh:
            raise CitSciConfigError("No refresh token available.")
        return {"refresh_token": self._refresh_token}  # type: ignore[dict-item]

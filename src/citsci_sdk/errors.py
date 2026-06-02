"""Exception hierarchy for the CitSci SDK.

Errors raised by the API are returned as RFC 7807 ``application/problem+json`` (the
``Error`` schema) or, for validation failures, the ``ConstraintViolation`` schema. This
module maps HTTP status codes to typed exceptions and extracts the problem details.
"""

from __future__ import annotations

from typing import Any


class CitSciError(Exception):
    """Base class for every error raised by the SDK."""


class CitSciConfigError(CitSciError):
    """Raised when the client is configured or used incorrectly (no network involved)."""


class CitSciAPIError(CitSciError):
    """Base class for errors returned by the CitSci API.

    Attributes:
        status_code: The HTTP status code.
        detail: The ``detail`` field from a problem+json body, when present.
        title: The ``title`` field from a problem+json body, when present.
        payload: The decoded JSON body, when present.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        detail: str | None = None,
        title: str | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
        self.title = title
        self.payload = payload


class AuthenticationError(CitSciAPIError):
    """401 — missing, invalid, or expired credentials."""


class PermissionDeniedError(CitSciAPIError):
    """403 — authenticated but not allowed to perform the action."""


class NotFoundError(CitSciAPIError):
    """404 — the requested resource does not exist."""


class ValidationError(CitSciAPIError):
    """422 — the request body failed server-side validation.

    Attributes:
        violations: The list of constraint violations (``propertyPath``/``message``)
            extracted from the ``violations`` field, when present.
    """

    def __init__(
        self, message: str, *, violations: list[dict[str, Any]] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.violations = violations or []


class RateLimitError(CitSciAPIError):
    """429 — too many requests."""


class ServerError(CitSciAPIError):
    """5xx — the API failed to handle the request."""


def _extract_body(body: Any) -> dict[str, Any]:
    return body if isinstance(body, dict) else {}


def error_from_response(status_code: int, body: Any) -> CitSciAPIError:
    """Build the appropriate :class:`CitSciAPIError` subclass from a response.

    *body* is the decoded JSON (``dict``) or ``None`` when the body was not JSON.
    """
    data = _extract_body(body)
    detail = data.get("detail") or data.get("hydra:description")
    title = data.get("title") or data.get("hydra:title")
    message = detail or title or f"HTTP {status_code}"

    common = {"status_code": status_code, "detail": detail, "title": title, "payload": body}

    if status_code == 401:
        return AuthenticationError(message, **common)
    if status_code == 403:
        return PermissionDeniedError(message, **common)
    if status_code == 404:
        return NotFoundError(message, **common)
    if status_code == 422:
        violations = data.get("violations")
        if not isinstance(violations, list):
            violations = None
        return ValidationError(message, violations=violations, **common)
    if status_code == 429:
        return RateLimitError(message, **common)
    if status_code >= 500:
        return ServerError(message, **common)
    return CitSciAPIError(message, **common)

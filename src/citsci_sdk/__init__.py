"""Citizen Science SDK — a Python client for the CitSci API (https://api.citsci.org).

Quick start::

    from citsci_sdk import CitSciClient

    with CitSciClient(email="me@example.com", password="…") as client:
        project = client.projects.get(123)
        for obs in client.observations.for_project(123, max_items=50):
            print(obs.observed_at)
"""

__version__ = "0.1.0"

# Imported after __version__ so that submodules (e.g. config) can read it.
from .client import CitSciClient  # noqa: E402
from .errors import (  # noqa: E402
    AuthenticationError,
    CitSciAPIError,
    CitSciConfigError,
    CitSciError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import (  # noqa: E402
    Area,
    Datasheet,
    DatasheetRecord,
    Observation,
    Project,
)

__all__ = [
    "__version__",
    "CitSciClient",
    # models
    "Area",
    "Datasheet",
    "DatasheetRecord",
    "Observation",
    "Project",
    # errors
    "CitSciError",
    "CitSciConfigError",
    "CitSciAPIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
]

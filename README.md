# citsci-sdk

A typed, synchronous Python client for the **[CitSci](https://www.citsci.org) API**
(<https://api.citsci.org>) — the citizen-science platform for creating projects, collecting
observations, and managing data.

- **Typed models** — Pydantic v2 models that mirror the CitSci API exactly, with full
  round-trip fidelity (camelCase wire fields ↔ snake_case Python attributes).
- **Auth handled for you** — log in with email + password and the client manages the JWT,
  refreshing or re-authenticating transparently on expiry.
- **Auto-pagination** — iterate entire collections without juggling page numbers.
- **Typed errors** — HTTP failures surface as specific exceptions (`NotFoundError`,
  `ValidationError`, …) carrying the server's problem details.
- **PPSR Core interchange** — export/import the standard
  [PPSR Core](https://github.com/arpieb/ppsr-core) models (PMM / ODM / DMM) for the resources
  that have a standard equivalent.

> **Note on PPSR Core.** CitSci is a member of the PPSR Core consortium that defined the
> standard, but its API does **not** use the PPSR Core data model internally. This SDK
> therefore models the API *natively* (so nothing is lost on read or write) and treats PPSR
> Core as a separate **interchange/export** layer rather than the primary representation.

## Requirements

- **Python ≥ 3.11**

## Installation

This package is not yet published to PyPI; install it from source.

```bash
# with uv (recommended)
uv add "git+https://github.com/arpieb/citsci-sdk.git"

# or with pip
pip install "git+https://github.com/arpieb/citsci-sdk.git"
```

The PPSR Core interchange dependency (`ppsr-core`) is installed automatically.

## Quick start

```python
from citsci_sdk import CitSciClient

with CitSciClient(email="me@example.com", password="…") as client:
    # Fetch a single project
    project = client.projects.get(123)
    print(project.name, project.description)

    # Stream every observation for that project (auto-paginated)
    for obs in client.observations.for_project(123, max_items=100):
        print(obs.observed_at, obs.lng_lat)
```

`CitSciClient` is a context manager; using `with` ensures the underlying HTTP connection is
closed. You can also call `client.close()` yourself.

## Authentication

Authenticate with credentials (the client logs in lazily on the first request) or with a token
you already hold:

```python
# Email + password — the client calls POST /login on demand and stores the JWT.
client = CitSciClient(email="me@example.com", password="…")

# Existing JWT (optionally with a refresh token).
client = CitSciClient(token="…", refresh_token="…")
```

On a `401` the client automatically tries the refresh token (`POST /token/refresh`); if that
fails and credentials are available, it re-logs-in — then retries the request once. The JWT is
sent as `Authorization: Bearer <token>`.

> Every CitSci endpoint requires authentication (including the "public" listings), so a client
> always needs either credentials or a token.

## Resources

Each resource namespace hangs off the client. Methods accept and return typed models.

| Namespace | Highlights |
|---|---|
| `client.projects` | `get`, `list`, `iterate`, `for_user`, `create`, `update`, `patch` |
| `client.observations` | `get`, `list`, `iterate`, `for_project`, `for_user`, `for_datasheet`, `for_area`, `create`, `update`, `patch`, `delete` |
| `client.datasheets` | `get`, `list`, `iterate`, `for_project`, `records`, `create`, `update`, `patch`, `delete` |
| `client.areas` | `get`, `for_project`, `create`, `update`, `delete` |

```python
from citsci_sdk import Observation

# Create — pass a model or a plain dict
new = client.observations.create(
    Observation(project="/projects/123", lng_lat="POINT(-105.1 40.5)")
)

# Partial update (sent as application/merge-patch+json)
client.observations.patch(new.id, {"is_private": True})

client.observations.delete(new.id)
```

Related resources (e.g. a project's `user`, an observation's `location`) are kept verbatim as
either an IRI string (`"/projects/123"`) or an embedded object, so writes echo back exactly what
the API expects.

### Filtering and pagination

CitSci collections are paginated with `page` / `itemsPerPage` (server-capped at **30**). Use
`list()` for a single page or `iterate()` to walk the whole collection:

```python
# One page
page = client.projects.list(page=1, items_per_page=10)

# Whole collection, lazily; stop early with max_items
for project in client.projects.iterate(max_items=250):
    ...
```

Filters map directly to the API's query-parameter names; pass them as keyword arguments (use a
dict for names containing dots or brackets):

```python
client.observations.iterate(**{"project.id": 123})
```

## Error handling

Non-2xx responses raise a subclass of `CitSciAPIError`, which carries `status_code`, `detail`,
`title`, and the decoded `payload`:

```python
from citsci_sdk import NotFoundError, ValidationError

try:
    client.projects.get(999_999)
except NotFoundError:
    print("no such project")

try:
    client.projects.create({"name": ""})
except ValidationError as exc:
    for v in exc.violations:        # [{"propertyPath": ..., "message": ...}, ...]
        print(v["propertyPath"], v["message"])
```

Exception hierarchy: `CitSciError` → `CitSciAPIError` → `AuthenticationError` (401),
`PermissionDeniedError` (403), `NotFoundError` (404), `ValidationError` (422),
`RateLimitError` (429), `ServerError` (5xx). `CitSciConfigError` is raised for client misuse
(no network involved).

## PPSR Core interchange

Convert the three resources that have a PPSR Core equivalent to/from the standard models:

| CitSci model | PPSR Core model |
|---|---|
| `Project` | `ppsr_core.Project` (Project Metadata Model) |
| `Observation` | `ppsr_core.ObservationBase` (Observation Data Model) |
| `Datasheet` | `ppsr_core.DatasetMetadata` (Dataset Metadata Model) |

```python
obs = client.observations.get(42)
standard = obs.to_ppsr_core()                 # -> ppsr_core.ObservationBase
roundtrip = Observation.from_ppsr_core(standard)
```

PPSR Core declares many required fields that the CitSci API never returns (controlled
vocabularies, contact points, responsible-party email, …). The mappers fill every field they
can and accept `**overrides` for the rest; if required fields are still missing, a
`CitSciConfigError` names exactly which keyword overrides to supply:

```python
project = client.projects.get(123)
standard = project.to_ppsr_core(
    project_status=...,            # ppsr_core.vocabularies.ProjectStatus
    project_science_type=...,
    contact_point=...,
    # ...the error message lists what's still needed
)
```

## Development

Managed with [uv](https://docs.astral.sh/uv/); the build backend is `uv_build`.

```bash
uv sync --extra dev        # install project + dev dependencies into .venv
uv run pytest              # run the test suite (coverage reported automatically)
uv run ruff check .        # lint
uv run ruff format .       # format
uv build                   # build sdist + wheel into dist/
```

Tests use [`respx`](https://lundberg.github.io/respx/) to mock HTTP, so the suite runs fully
offline.

## Status

The client transport (auth, errors, pagination) and the core resources — projects,
observations, datasheets, and areas (locations) — are implemented. The remaining API surface
(hubs/organizations, notifications, file objects, users, organisms, stats, …) follows the same
patterns and can be added incrementally. For endpoints not yet wrapped, drop down to the raw
transport:

```python
data = client.request("GET", "/organisms", params={"page": 1})
```

## License

[MIT](LICENSE)

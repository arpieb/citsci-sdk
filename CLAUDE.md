# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

A synchronous Python client for the **CitSci API** (https://api.citsci.org), an API Platform
(Symfony) service documented at `https://api.citsci.org/docs.jsonopenapi?index=index`. "citsci"
= citizen science. The foundation + core resources are implemented; remaining resources (hubs,
notifications, files, users, etc.) follow the same patterns.

Key design point: **CitSci helped define the PPSR Core standard but does not use it in its own
API.** So the SDK models the API natively (camelCase fields → snake_case attrs, full round-trip
fidelity) and offers **PPSR Core as an optional interchange/export layer** (`pip install
citsci-sdk[ppsr]`), not as the primary model type.

## Architecture

- **Auth** (`auth.py` + `http.py`): JWT via `POST /login`; `TokenAuth` holds credentials/tokens,
  `Transport` logs in on demand and, on a `401`, refreshes (`POST /token/refresh`) or re-logs-in
  and retries once. Token goes in the `Authorization: Bearer <jwt>` header. *All* API operations
  require auth (no public-read override in the spec).
- **Transport** (`http.py`): the only place that touches `httpx`. Serializes JSON bodies
  (merge-patch for PATCH), maps non-2xx → typed errors (`errors.py`).
- **Pagination** (`pagination.py`): Hydra `page`/`itemsPerPage` (capped at 30). Plain JSON
  collections are bare arrays with no total, so `iterate()` walks pages until a short/empty page.
- **Models** (`models/`): `CitSciModel` base (camelCase alias gen, `extra="allow"`). Native models
  mirror API fields exactly; related resources are kept as IRI strings or nested dicts (`Reference`).
- **Resources** (`resources/`): `BaseResource[M]` provides generic CRUD/list/iterate; namespaces
  `projects`, `observations`, `datasheets`, `areas` hang off `CitSciClient`.
- **Interchange** (`interchange/ppsr.py`): best-effort `*_to_ppsr_core()`/`*_from_ppsr_core()` for
  Project↔`ppsr_core.Project`, Observation↔`ObservationBase`, Datasheet↔`DatasetMetadata`. Lazy
  imports `ppsr_core`; raises a clear error naming missing required fields to pass as overrides.

## Layout

- `src/citsci_sdk/` — the SDK package (src layout; importable as `citsci_sdk`).
- `tests/` — pytest suite (mocked with `respx`; no network).
- `pyproject.toml` — project metadata, build backend, deps, dev deps, and test/coverage/ruff
  config. Requires **Python >=3.11** (CI runs 3.11–3.14; avoid 3.12+-only syntax such as PEP 695
  generics — use `TypeVar`/`Generic`).

## Tooling & commands

Managed with **uv**; the build backend is **uv_build**. Runtime deps: `httpx`, `pydantic`. Dev
deps (pytest, pytest-cov, ruff, pre-commit, respx) live in the `dev` group. The `ppsr` extra
pulls `ppsr-core` from git for interchange.

- `uv sync --extra ppsr --extra dev` — install the project, interchange extra, and dev deps.
- `uv sync` — install the project and dev dependencies into `.venv`.
- `uv run pytest` — run the full test suite (coverage on `citsci_sdk` is reported automatically via `addopts`).
- `uv run pytest tests/test_smoke.py::test_version` — run a single test.
- `uv build` — build sdist + wheel into `dist/`.

Coverage is configured (branch coverage, `--cov-report=term-missing`) in `pyproject.toml`; no separate coverage invocation is needed.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early-stage SDK. The `citsci_sdk` package currently exposes only `__version__`; build out the API from here. "citsci" = citizen science — this is intended as a client/SDK library.

## Layout

- `src/citsci_sdk/` — the SDK package (src layout; importable as `citsci_sdk`).
- `tests/` — pytest suite.
- `pyproject.toml` — project metadata, build backend, dev dependency group, and test/coverage config. Requires **Python >=3.14**.

## Tooling & commands

Managed with **uv**; the build backend is **uv_build**. Dev dependencies (pytest, pytest-cov) live in the `dev` dependency group.

- `uv sync` — install the project and dev dependencies into `.venv`.
- `uv run pytest` — run the full test suite (coverage on `citsci_sdk` is reported automatically via `addopts`).
- `uv run pytest tests/test_smoke.py::test_version` — run a single test.
- `uv build` — build sdist + wheel into `dist/`.

Coverage is configured (branch coverage, `--cov-report=term-missing`) in `pyproject.toml`; no separate coverage invocation is needed.

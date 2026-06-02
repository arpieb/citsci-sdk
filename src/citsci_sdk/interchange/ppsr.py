"""Mappers between CitSci-native models and PPSR Core models.

The ``ppsr_core`` package is imported lazily so the base SDK has no dependency on it. The
mappings cover the fields that genuinely overlap; everything else is either supplied by
the caller via ``**overrides`` or left to the PPSR Core model's defaults.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from ..errors import CitSciConfigError
from ..models.datasheet import Datasheet
from ..models.observation import Observation
from ..models.project import Project

if TYPE_CHECKING:  # pragma: no cover - typing only
    import ppsr_core


def _ppsr() -> Any:
    """Import and return the ``ppsr_core`` module, or raise a helpful error."""
    try:
        import ppsr_core
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise CitSciConfigError(
            "PPSR Core interchange requires the optional 'ppsr' extra. "
            "Install it with: pip install citsci-sdk[ppsr]"
        ) from exc
    return ppsr_core


def _build(model_cls: type, fields: dict[str, Any], overrides: dict[str, Any]) -> Any:
    """Construct a PPSR Core model, dropping ``None``s and applying overrides.

    Re-raises pydantic validation failures as a :class:`CitSciConfigError` that names the
    fields CitSci could not supply, so the caller knows exactly what to pass as overrides.
    """
    from pydantic import ValidationError as PydanticValidationError

    data = {k: v for k, v in fields.items() if v is not None}
    data.update(overrides)
    try:
        return model_cls(**data)
    except PydanticValidationError as exc:
        # Validation error `loc` uses the model's (camelCase) alias; translate back to the
        # snake_case attribute names callers actually pass as overrides.
        name_by_alias = {(f.alias or name): name for name, f in model_cls.model_fields.items()}
        missing = sorted(
            {
                name_by_alias.get(str(e["loc"][0]), str(e["loc"][0]))
                for e in exc.errors()
                if e["loc"]
            }
        )
        raise CitSciConfigError(
            f"Cannot build {model_cls.__name__}: the CitSci API does not supply "
            f"{missing}. Pass them as keyword overrides, e.g. "
            f"{model_cls.__name__.lower()}_to_ppsr_core(obj, {missing[0]}=...)."
        ) from exc


def _coords_from_lng_lat(lng_lat: str | None) -> tuple[float | None, float | None]:
    """Parse a CitSci ``lngLat`` string into ``(longitude, latitude)``.

    Accepts WKT ``POINT(lon lat)`` or a delimited ``lon,lat`` / ``lon lat`` pair. Returns
    ``(None, None)`` when it cannot be parsed.
    """
    if not lng_lat:
        return None, None
    numbers = re.findall(r"-?\d+(?:\.\d+)?", lng_lat)
    if len(numbers) < 2:
        return None, None
    return float(numbers[0]), float(numbers[1])


def _lng_lat_from_coords(longitude: float | None, latitude: float | None) -> str | None:
    if longitude is None or latitude is None:
        return None
    return f"POINT({longitude} {latitude})"


# -- Project (PMM) ----------------------------------------------------------------


def project_to_ppsr_core(project: Project, **overrides: Any) -> ppsr_core.Project:
    """Map a CitSci :class:`Project` to a ``ppsr_core.Project`` (best effort)."""
    ppsr = _ppsr()
    fields = {
        "project_id": None if project.id is None else str(project.id),
        "project_name": project.name,
        "project_aim": project.goals,
        "project_description": project.description,
        "project_url": project.url_field or project.website,
        "project_date_created": project.created_at,
        "project_last_updated_date": project.updated_at,
    }
    return _build(ppsr.Project, fields, overrides)


def project_from_ppsr_core(source: ppsr_core.Project) -> Project:
    """Map a ``ppsr_core.Project`` back to a CitSci :class:`Project` (overlapping fields)."""
    return Project(
        id=_as_str(source.project_id),
        name=source.project_name,
        goals=source.project_aim,
        description=source.project_description,
        url_field=str(source.project_url) if source.project_url else None,
        created_at=source.project_date_created,
        updated_at=source.project_last_updated_date,
    )


# -- Observation (ODM) ------------------------------------------------------------


def observation_to_ppsr_core(
    observation: Observation, **overrides: Any
) -> ppsr_core.ObservationBase:
    """Map a CitSci :class:`Observation` to a ``ppsr_core.ObservationBase``."""
    ppsr = _ppsr()
    longitude, latitude = _coords_from_lng_lat(observation.lng_lat)
    fields = {
        "observation_id": None if observation.id is None else str(observation.id),
        "event_date": observation.observed_at,
        "decimal_latitude": latitude,
        "decimal_longitude": longitude,
    }
    return _build(ppsr.ObservationBase, fields, overrides)


def observation_from_ppsr_core(source: ppsr_core.ObservationBase) -> Observation:
    """Map a ``ppsr_core.ObservationBase`` back to a CitSci :class:`Observation`."""
    return Observation(
        id=_as_str(source.observation_id),
        observed_at=source.event_date,
        lng_lat=_lng_lat_from_coords(source.decimal_longitude, source.decimal_latitude),
    )


# -- Datasheet (DMM) --------------------------------------------------------------


def datasheet_to_ppsr_core(datasheet: Datasheet, **overrides: Any) -> ppsr_core.DatasetMetadata:
    """Map a CitSci :class:`Datasheet` to a ``ppsr_core.DatasetMetadata``."""
    ppsr = _ppsr()
    fields = {
        "identifier": None if datasheet.id is None else str(datasheet.id),
        "title": datasheet.name,
        "abstract": datasheet.instructions,
        "date_submitted": datasheet.created_at,
        "modified": datasheet.updated_at,
        "project_id": _reference_id(datasheet.project),
    }
    return _build(ppsr.DatasetMetadata, fields, overrides)


def datasheet_from_ppsr_core(source: ppsr_core.DatasetMetadata) -> Datasheet:
    """Map a ``ppsr_core.DatasetMetadata`` back to a CitSci :class:`Datasheet`."""
    return Datasheet(
        id=_as_str(source.identifier),
        name=source.title,
        instructions=source.abstract,
        created_at=source.date_submitted,
        updated_at=source.modified,
    )


# -- helpers ----------------------------------------------------------------------


def _as_str(value: Any) -> str | None:
    """CitSci resource ids are UUID strings; preserve them as-is (None stays None)."""
    return None if value is None else str(value)


def _reference_id(ref: Any) -> str | None:
    """Extract an id from an IRI string (``/projects/42``) or embedded dict."""
    if isinstance(ref, str):
        tail = ref.rstrip("/").rsplit("/", 1)[-1]
        return tail or None
    if isinstance(ref, dict):
        value = ref.get("id") or ref.get("@id")
        return None if value is None else str(value)
    return None

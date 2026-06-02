"""CitSci-native data models.

These Pydantic v2 models mirror the CitSci API resource shapes exactly (camelCase fields,
related resources as IRIs or nested objects) so that data round-trips through the API
without loss. For interchange with the PPSR Core standard, see
:mod:`citsci_sdk.interchange`.
"""

from .area import Area
from .base import CitSciModel, Reference
from .datasheet import Datasheet, DatasheetRecord
from .observation import Observation
from .project import Project

__all__ = [
    "CitSciModel",
    "Reference",
    "Area",
    "Datasheet",
    "DatasheetRecord",
    "Observation",
    "Project",
]

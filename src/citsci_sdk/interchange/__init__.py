"""Interchange between CitSci-native models and the PPSR Core data standard.

CitSci helped define PPSR Core but does **not** use it in its own API, so the two model
families have different fields. This package provides best-effort mappers for the three
resources that have a PPSR Core equivalent:

* CitSci :class:`~citsci_sdk.models.project.Project` ↔ ``ppsr_core.Project`` (PMM)
* CitSci :class:`~citsci_sdk.models.observation.Observation` ↔ ``ppsr_core.ObservationBase`` (ODM)
* CitSci :class:`~citsci_sdk.models.datasheet.Datasheet` ↔ ``ppsr_core.DatasetMetadata`` (DMM)

PPSR Core models declare many required fields the CitSci API never returns (controlled
vocabularies, contact points, responsible-party email, …). The ``*_to_ppsr_core`` helpers
map every field they can and accept ``**overrides`` to supply the rest; if required fields
are still missing, a clear :class:`~citsci_sdk.errors.CitSciConfigError` is raised listing
them. Requires the ``ppsr`` extra: ``pip install citsci-sdk[ppsr]``.
"""

from .ppsr import (
    datasheet_from_ppsr_core,
    datasheet_to_ppsr_core,
    observation_from_ppsr_core,
    observation_to_ppsr_core,
    project_from_ppsr_core,
    project_to_ppsr_core,
)

__all__ = [
    "project_to_ppsr_core",
    "project_from_ppsr_core",
    "observation_to_ppsr_core",
    "observation_from_ppsr_core",
    "datasheet_to_ppsr_core",
    "datasheet_from_ppsr_core",
]

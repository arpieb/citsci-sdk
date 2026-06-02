"""Resource namespaces exposed on :class:`~citsci_sdk.client.CitSciClient`."""

from .areas import AreasResource
from .datasheets import DatasheetsResource
from .observations import ObservationsResource
from .projects import ProjectsResource

__all__ = [
    "AreasResource",
    "DatasheetsResource",
    "ObservationsResource",
    "ProjectsResource",
]

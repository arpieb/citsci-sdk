"""PPSR Core interchange (requires the `ppsr` extra, installed in dev)."""

from datetime import datetime

import pytest

from citsci_sdk import Datasheet, Observation, Project
from citsci_sdk.errors import CitSciConfigError
from citsci_sdk.interchange.ppsr import _coords_from_lng_lat


@pytest.mark.parametrize(
    "value,expected",
    [
        ("POINT(-105.1 40.5)", (-105.1, 40.5)),
        ("-105.1,40.5", (-105.1, 40.5)),
        ("-105.1 40.5", (-105.1, 40.5)),
        (None, (None, None)),
        ("garbage", (None, None)),
    ],
)
def test_coords_parsing(value, expected):
    assert _coords_from_lng_lat(value) == expected


def test_observation_round_trips_through_ppsr_core():
    obs = Observation(
        id=10,
        observed_at=datetime.fromisoformat("2024-05-01T12:00:00+00:00"),
        lng_lat="POINT(-105.1 40.5)",
    )
    std = obs.to_ppsr_core()

    assert std.observation_id == "10"
    assert std.event_date == obs.observed_at
    assert std.decimal_longitude == -105.1
    assert std.decimal_latitude == 40.5

    back = Observation.from_ppsr_core(std)
    assert back.id == 10
    assert back.lng_lat == "POINT(-105.1 40.5)"
    assert back.observed_at == obs.observed_at


def test_to_ppsr_core_reports_missing_required_fields():
    # PPSR Core's Project requires controlled vocabularies / contact info the CitSci API
    # never supplies, so conversion without overrides raises a helpful error.
    project = Project(id=1, name="Birds", goals="count", description="desc")
    with pytest.raises(CitSciConfigError) as exc:
        project.to_ppsr_core()
    msg = str(exc.value)
    assert "Project" in msg
    # Missing required fields are reported by their snake_case override name.
    assert "project_status" in msg
    assert "contact_point" in msg


def test_datasheet_extracts_project_id_from_iri():
    from citsci_sdk.interchange.ppsr import _reference_id

    assert _reference_id("/projects/42") == "42"
    assert _reference_id({"id": 7}) == "7"
    assert _reference_id(None) is None

    ds = Datasheet(id=3, name="Form", instructions="how", project="/projects/42")
    with pytest.raises(CitSciConfigError):
        # DatasetMetadata also has required fields beyond the overlap; just confirm the
        # mapper runs and surfaces the missing ones rather than crashing on project_id.
        ds.to_ppsr_core()

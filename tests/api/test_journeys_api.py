
from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.flight_event import FlightEvent


def _utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def _event(
    flight_number: str,
    from_city: str,
    to_city: str,
    depart: datetime,
    arrive: datetime,
) -> FlightEvent:
    return FlightEvent(
        flight_number=flight_number,
        departure_city=from_city,
        arrival_city=to_city,
        departure_datetime=depart,
        arrival_datetime=arrive,
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_search_journeys_happy_path(client: TestClient) -> None:
    direct = _event(
        "IB100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 8, 0),
        _utc(2026, 9, 12, 20, 0),
    )
    leg1 = _event(
        "AR200",
        "BUE",
        "GRU",
        _utc(2026, 9, 12, 9, 0),
        _utc(2026, 9, 12, 11, 0),
    )
    leg2 = _event(
        "IB201",
        "GRU",
        "MAD",
        _utc(2026, 9, 12, 13, 0),
        _utc(2026, 9, 12, 23, 0),
    )
    mock_events = [direct, leg1, leg2]

    with patch("app.api.journeys.get_flight_events", return_value=mock_events):
        response = client.get(
            "/journeys/search?date=2026-09-12&from=BUE&to=MAD"
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    connections = [journey["connections"] for journey in data]
    assert 1 in connections
    assert 2 in connections
    for journey in data:
        assert "connections" in journey
        assert "path" in journey
        assert isinstance(journey["path"], list)
        assert len(journey["path"]) == journey["connections"]
        for segment in journey["path"]:
            assert "flight_number" in segment
            assert "from" in segment
            assert "to" in segment
            assert "departure_time" in segment
            assert "arrival_time" in segment


def test_search_journeys_no_results(client: TestClient) -> None:
    with patch("app.api.journeys.get_flight_events", return_value=[]):
        response = client.get(
            "/journeys/search?date=2026-09-12&from=BUE&to=MAD"
        )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "query",
    [
        "/journeys/search?from=BUE&to=MAD",
        "/journeys/search?date=2026-09-12&to=MAD",
        "/journeys/search?date=2026-09-12&from=BUE",
    ],
)
def test_search_journeys_validation_errors(client: TestClient, query: str) -> None:
    response = client.get(query)
    assert response.status_code == 422

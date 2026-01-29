from datetime import date, datetime, timezone

import pytest

from app.models.flight_event import FlightEvent
from app.services.journey_search import JourneySearchService


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
def service() -> JourneySearchService:
    return JourneySearchService()


def test_direct_flight_returned_when_origin_destination_date_match(
    service: JourneySearchService,
) -> None:
    events = [
        _event(
            "XX100",
            "BUE",
            "MAD",
            _utc(2026, 9, 12, 12, 0),
            _utc(2026, 9, 13, 0, 0),
        ),
    ]
    results = service.search(date(2026, 9, 12), "BUE", "MAD", events)
    assert len(results) == 1
    assert results[0].connections == 1
    assert len(results[0].path) == 1
    assert results[0].path[0].flight_number == "XX100"
    assert results[0].path[0].from_ == "BUE"
    assert results[0].path[0].to == "MAD"


def test_valid_two_leg_journey_returned(service: JourneySearchService) -> None:
    leg1 = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 12, 0),
        _utc(2026, 9, 13, 0, 0),
    )
    leg2 = _event(
        "XX200",
        "MAD",
        "PMI",
        _utc(2026, 9, 13, 2, 0),
        _utc(2026, 9, 13, 3, 0),
    )
    events = [leg1, leg2]
    results = service.search(date(2026, 9, 12), "BUE", "PMI", events)
    assert len(results) == 1
    assert results[0].connections == 2
    assert len(results[0].path) == 2
    assert results[0].path[0].flight_number == "XX100"
    assert results[0].path[1].flight_number == "XX200"


def test_two_leg_journey_with_connection_over_four_hours_rejected(
    service: JourneySearchService,
) -> None:
    leg1 = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 12, 0),
        _utc(2026, 9, 12, 20, 0),
    )
    leg2 = _event(
        "XX200",
        "MAD",
        "PMI",
        _utc(2026, 9, 13, 1, 0),
        _utc(2026, 9, 13, 2, 0),
    )
    events = [leg1, leg2]
    results = service.search(date(2026, 9, 12), "BUE", "PMI", events)
    assert len(results) == 0


def test_two_leg_journey_with_total_duration_over_24_hours_rejected(
    service: JourneySearchService,
) -> None:
    leg1 = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 0, 0),
        _utc(2026, 9, 12, 2, 0),
    )
    leg2 = _event(
        "XX200",
        "MAD",
        "PMI",
        _utc(2026, 9, 12, 4, 0),
        _utc(2026, 9, 13, 1, 0),
    )
    events = [leg1, leg2]
    results = service.search(date(2026, 9, 12), "BUE", "PMI", events)
    assert len(results) == 0


def test_journeys_with_incorrect_connecting_cities_rejected(
    service: JourneySearchService,
) -> None:
    leg1 = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 12, 0),
        _utc(2026, 9, 13, 0, 0),
    )
    leg2 = _event(
        "XX200",
        "BCN",
        "PMI",
        _utc(2026, 9, 13, 2, 0),
        _utc(2026, 9, 13, 3, 0),
    )
    events = [leg1, leg2]
    results = service.search(date(2026, 9, 12), "BUE", "PMI", events)
    assert len(results) == 0


def test_duplicate_flight_combinations_appear_only_once(
    service: JourneySearchService,
) -> None:
    leg1 = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 12, 0),
        _utc(2026, 9, 13, 0, 0),
    )
    leg2 = _event(
        "XX200",
        "MAD",
        "PMI",
        _utc(2026, 9, 13, 2, 0),
        _utc(2026, 9, 13, 3, 0),
    )
    events = [leg1, leg2, leg1, leg2]
    results = service.search(date(2026, 9, 12), "BUE", "PMI", events)
    assert len(results) == 1
    assert results[0].connections == 2


def test_results_ordered_by_first_departure_time_ascending(
    service: JourneySearchService,
) -> None:
    late = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 20, 0),
        _utc(2026, 9, 13, 8, 0),
    )
    early = _event(
        "XX200",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 8, 0),
        _utc(2026, 9, 12, 18, 0),
    )
    events = [late, early]
    results = service.search(date(2026, 9, 12), "BUE", "MAD", events)
    assert len(results) == 2
    assert results[0].path[0].departure_time == _utc(2026, 9, 12, 8, 0)
    assert results[1].path[0].departure_time == _utc(2026, 9, 12, 20, 0)


def test_flights_not_departing_from_origin_are_ignored(
    service: JourneySearchService,
) -> None:
    events = [
        _event(
            "XX999",
            "BCN",
            "MAD",
            _utc(2026, 9, 12, 8, 0),
            _utc(2026, 9, 12, 10, 0),
        )
    ]
    results = service.search(date(2026, 9, 12), "BUE", "MAD", events)
    assert results == []


def test_departure_time_is_timezone_aware(service: JourneySearchService) -> None:
    event = _event(
        "XX100",
        "BUE",
        "MAD",
        _utc(2026, 9, 12, 8, 0),
        _utc(2026, 9, 12, 20, 0),
    )
    result = service.search(date(2026, 9, 12), "BUE", "MAD", [event])[0]
    assert result.path[0].departure_time.tzinfo is timezone.utc

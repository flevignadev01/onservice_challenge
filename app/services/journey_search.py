from datetime import date, datetime, timedelta

from app.models.flight_event import FlightEvent
from app.schemas.journey import FlightPathSegment, JourneySearchResult

MAX_JOURNEY_DURATION_HOURS = 24
MAX_CONNECTION_HOURS = 4


def _event_to_segment(event: FlightEvent) -> FlightPathSegment:
    """Map a FlightEvent to a FlightPathSegment schema."""
    return FlightPathSegment(
        flight_number=event.flight_number,
        from_=event.departure_city,
        to=event.arrival_city,
        departure_time=event.departure_datetime,
        arrival_time=event.arrival_datetime,
    )


def _total_duration_within_limit(
    first_departure: datetime,
    last_arrival: datetime,
) -> bool:
    """Return True if journey duration (first departure to last arrival) is <= 24 hours."""
    delta = last_arrival - first_departure
    return delta <= timedelta(hours=MAX_JOURNEY_DURATION_HOURS)


def _connection_within_limit(
    first_arrival: datetime,
    second_departure: datetime,
) -> bool:
    """Return True if connection time between flights is <= 4 hours."""
    delta = second_departure - first_arrival
    return timedelta(0) <= delta <= timedelta(hours=MAX_CONNECTION_HOURS)


class JourneySearchService:
    """Service that finds valid journeys from flight events."""

    def search(
        self,
        date: date,
        origin: str,
        destination: str,
        events: list[FlightEvent],
    ) -> list[JourneySearchResult]:
        """
        Find all journeys from origin to destination departing on the given date.

        Assumptions:
            - FlightEvent datetimes are timezone-aware and normalized to UTC.

        - Journey is 1 or 2 flight events.
        - First flight departs on the given date (UTC).
        - Cities connect (for 2 legs: first arrival_city == second departure_city).
        - Total duration (first departure to last arrival) <= 24 hours.
        - Connection time between two flights <= 4 hours.

        Returns a list of JourneySearchResult (schemas), not persistence models.
        """
        origin = origin.strip().upper()
        destination = destination.strip().upper()
        results: list[JourneySearchResult] = []
        seen: set[tuple[str, ...]] = set()

        # Direct flights (1 leg)
        for event in events:
            if (
                event.departure_city == origin
                and event.arrival_city == destination
                and event.departure_datetime.date() == date
            ):
                if _total_duration_within_limit(
                    event.departure_datetime,
                    event.arrival_datetime,
                ):
                    key = (event.flight_number,)
                    if key not in seen:
                        seen.add(key)
                        segment = _event_to_segment(event)
                        results.append(
                            JourneySearchResult(connections=1, path=[segment])
                        )

        # Connecting flights (2 legs)
        for first in events:
            if (
                first.departure_city != origin
                or first.arrival_city == destination
                or first.departure_datetime.date() != date
            ):
                continue

            for second in events:
                if (
                    second.departure_city != first.arrival_city
                    or second.arrival_city != destination
                    or second.departure_datetime <= first.arrival_datetime
                ):
                    continue
                if not _connection_within_limit(
                    first.arrival_datetime,
                    second.departure_datetime,
                ):
                    continue
                if not _total_duration_within_limit(
                    first.departure_datetime,
                    second.arrival_datetime,
                ):
                    continue

                key = (first.flight_number, second.flight_number)
                if key not in seen:
                    seen.add(key)
                    path = [
                        _event_to_segment(first),
                        _event_to_segment(second),
                    ]
                    results.append(JourneySearchResult(connections=2, path=path))

        results.sort(key=lambda r: r.path[0].departure_time)
        return results

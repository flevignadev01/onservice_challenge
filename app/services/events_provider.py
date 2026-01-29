from datetime import datetime, timezone

from app.models.flight_event import FlightEvent


def get_flight_events() -> list[FlightEvent]:
    """
    Return flight events for the given date.

    This simulates an external Flight Events API.
    The data is deterministic and suitable for local development and testing.
    """

    return [
        # --- Direct flight BUE -> MAD ---
        FlightEvent(
            flight_number="IB100",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=datetime(2026, 9, 12, 8, 0, tzinfo=timezone.utc),
            arrival_datetime=datetime(2026, 9, 12, 20, 0, tzinfo=timezone.utc),
        ),
        # --- First leg BUE -> GRU ---
        FlightEvent(
            flight_number="AR200",
            departure_city="BUE",
            arrival_city="GRU",
            departure_datetime=datetime(2026, 9, 12, 9, 0, tzinfo=timezone.utc),
            arrival_datetime=datetime(2026, 9, 12, 11, 0, tzinfo=timezone.utc),
        ),
        # --- Second leg GRU -> MAD (valid connection: 2h layover) ---
        FlightEvent(
            flight_number="IB201",
            departure_city="GRU",
            arrival_city="MAD",
            departure_datetime=datetime(2026, 9, 12, 13, 0, tzinfo=timezone.utc),
            arrival_datetime=datetime(2026, 9, 12, 23, 0, tzinfo=timezone.utc),
        ),
        # --- Invalid connection (too long layover, should be ignored) ---
        FlightEvent(
            flight_number="IB999",
            departure_city="GRU",
            arrival_city="MAD",
            departure_datetime=datetime(2026, 9, 12, 20, 30, tzinfo=timezone.utc),
            arrival_datetime=datetime(2026, 9, 13, 6, 0, tzinfo=timezone.utc),
        ),
    ]

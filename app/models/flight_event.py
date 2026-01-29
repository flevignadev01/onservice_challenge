from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class FlightEvent(BaseModel):
    """
    Domain model representing a flight event.

    Used in memory by the events provider and journey search service.
    All datetimes are UTC and timezone-aware.
    """

    flight_number: str = Field(description="Flight number")
    departure_city: str = Field(
        min_length=3,
        max_length=3,
        description="Origin city code (3-letter IATA code)",
    )
    arrival_city: str = Field(
        min_length=3,
        max_length=3,
        description="Destination city code (3-letter IATA code)",
    )
    departure_datetime: datetime = Field(
        description="Departure date and time in UTC",
    )
    arrival_datetime: datetime = Field(
        description="Arrival date and time in UTC",
    )

    @field_validator("departure_datetime", "arrival_datetime")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime) -> datetime:
        """Ensure datetime is timezone-aware and convert to UTC."""
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware and expressed in UTC")
        return value.astimezone(timezone.utc)

    @field_validator("arrival_datetime")
    @classmethod
    def arrival_after_departure(cls, arrival: datetime, info) -> datetime:
        """Ensure arrival time is after departure time."""
        departure = info.data.get("departure_datetime")
        if departure and arrival <= departure:
            raise ValueError("Arrival must be after departure")
        return arrival

    model_config = {
        "json_schema_extra": {
            "example": {
                "flight_number": "IB1234",
                "departure_city": "MAD",
                "arrival_city": "BUE",
                "departure_datetime": "2021-12-31T23:59:59Z",
                "arrival_datetime": "2022-01-01T00:00:00Z",
            }
        }
    }

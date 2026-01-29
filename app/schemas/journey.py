from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_serializer, field_validator


def _serialize_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


class FlightPathSegment(BaseModel):
    """Single flight segment in a journey."""

    flight_number: str = Field(description="Flight number")
    from_: str = Field(
        alias="from",
        min_length=3,
        max_length=3,
        description="Origin city code (3-letter IATA)",
    )
    to: str = Field(
        min_length=3,
        max_length=3,
        description="Destination city code (3-letter IATA)",
    )
    departure_time: datetime = Field(description="Departure date and time (UTC)")
    arrival_time: datetime = Field(description="Arrival date and time (UTC)")

    @field_validator("departure_time", "arrival_time")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        """Ensure datetime is timezone-aware and convert to UTC."""
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware and expressed in UTC")
        return value.astimezone(timezone.utc)

    @field_serializer("departure_time", "arrival_time")
    def serialize_datetime(self, dt: datetime) -> str:
        return _serialize_datetime(dt)

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "flight_number": "XX1234",
                "from": "BUE",
                "to": "MAD",
                "departure_time": "2024-09-12 12:00",
                "arrival_time": "2024-09-13 00:00",
            }
        },
    }


class JourneySearchResult(BaseModel):
    """Single journey: sequence of flight segments connecting origin to destination."""

    connections: int = Field(
        ge=1,
        le=2,
        description="Number of flight segments in the journey (1 or 2 for this version)",
    )
    path: list[FlightPathSegment] = Field(
        description="Ordered sequence of flight segments",
        min_length=1,
        max_length=2,
    )

    @field_validator("connections")
    @classmethod
    def validate_connections(cls, v: int, info) -> int:
        """Ensure connections count matches path length."""
        path = info.data.get("path")
        if path and v != len(path):
            raise ValueError("connections must equal path length")
        return v

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "connections": 2,
                "path": [
                    {
                        "flight_number": "XX1234",
                        "from": "BUE",
                        "to": "MAD",
                        "departure_time": "2024-09-12 12:00",
                        "arrival_time": "2024-09-13 00:00",
                    },
                    {
                        "flight_number": "XX2345",
                        "from": "MAD",
                        "to": "PMI",
                        "departure_time": "2024-09-13 02:00",
                        "arrival_time": "2024-09-13 03:00",
                    },
                ],
            }
        },
    }


JourneySearchResponse = list[JourneySearchResult]

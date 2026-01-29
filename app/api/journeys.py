from datetime import date

from fastapi import APIRouter, Query

from app.schemas import JourneySearchResponse
from app.services.events_provider import get_flight_events
from app.services.journey_search import JourneySearchService

router = APIRouter()


@router.get(
    "/search",
    response_model=JourneySearchResponse,
    summary="Search journeys",
    description="Returns journeys from origin to destination departing on the given date.",
)
def search_journeys(
    date_param: date = Query(
        ..., alias="date", description="Departure date (YYYY-MM-DD)"
    ),
    from_code: str = Query(
        ...,
        alias="from",
        min_length=3,
        max_length=3,
        description="Origin city code (3-letter IATA)",
    ),
    to_code: str = Query(
        ...,
        alias="to",
        min_length=3,
        max_length=3,
        description="Destination city code (3-letter IATA)",
    ),
) -> JourneySearchResponse:
    service = JourneySearchService()
    events = get_flight_events()
    return service.search(date_param, from_code, to_code, events)

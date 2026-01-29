# Flight Journey Search API

A Python FastAPI service that searches for flight journeys connecting origin and destination cities on a given departure date.

## Project Overview

This API solves the problem of finding valid flight journeys from a collection of flight events. A journey is a sequence of 1 or 2 flight events that connects an origin city to a destination city, departing on a specified date.

Journey constraints:
- Maximum 2 flight segments per journey
- Total journey duration (first departure to last arrival) must not exceed 24 hours
- Connection time between two flights must not exceed 4 hours
- All datetimes are expressed in UTC and must be timezone-aware

## Architecture Overview

The project follows a layered architecture with clear separation of concerns:

- **`app/api/`** – FastAPI route handlers. Contains no business logic; delegates to services.
- **`app/services/`** – Business logic layer. `JourneySearchService` implements journey search algorithms. `events_provider` simulates a third-party Flight Events API via an in-memory implementation.
- **`app/models/`** – Domain models (Pydantic). `FlightEvent` represents a single flight instance.
- **`app/schemas/`** – API response schemas (Pydantic). Defines the structure of journey search responses.
- **`app/core/`** – Application configuration and settings.

Persistence was intentionally omitted. Flight events are provided by an in-memory provider (`get_flight_events`) that simulates an external API. This design allows the business logic to be tested independently and makes it straightforward to replace the provider with a real HTTP client or database integration in the future. This approach keeps the core journey search logic deterministic, easy to test, and independent from infrastructure concerns.

## Project Structure

```
app/
├── api/            # FastAPI route handlers
├── services/       # Business logic
├── models/         # Domain models
├── schemas/        # API schemas
├── core/           # Settings and configuration
└── main.py

tests/
├── api/            # API integration tests
└── services/       # Unit tests
```

## Requirements

- Python 3.11 or higher
- Dependencies listed in `requirements.txt`:
  - FastAPI
  - Pydantic v2 (via FastAPI)
  - pydantic-settings (used to centralize application configuration—environment, defaults—even though no external services are required in this version)
  - uvicorn
- Docker Desktop (Optional for containerized execution)
  - Windows / macOS / Linux

### Runtime and dev dependencies

Runtime dependencies are in `requirements.txt`; dev dependencies are intentionally separated into `requirements-dev.txt`.  
Dev dependencies include:

- pytest
- pytest-cov
- httpx (required by FastAPI TestClient)

## How to Run the API

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.


## Running with Docker (Optional)

This project can also be run as a Docker container. This is optional and provided for portability and reproducible execution across environments.

### Prerequisites

- Docker Desktop installed and running

### Build the image

1. From the project root:

```bash
  docker build -t flight-journey-api .
 ```

2. Run the container

```bash
  docker run -p 8000:8000 flight-journey-api
 ```

3. The API will be available at:

``` 
  http://127.0.0.1:8000
```

## Example API Request

Search for journeys from Buenos Aires (BUE) to Madrid (MAD) on September 12, 2026:

```bash
  curl "http://127.0.0.1:8000/journeys/search?date=2026-09-12&from=BUE&to=MAD"
```

Example response (direct flight and connecting journey):

```json
[
  {
    "connections": 1,
    "path": [
      {
        "flight_number": "IB100",
        "from": "BUE",
        "to": "MAD",
        "departure_time": "2026-09-12 08:00",
        "arrival_time": "2026-09-12 20:00"
      }
    ]
  },
  {
    "connections": 2,
    "path": [
      {
        "flight_number": "AR200",
        "from": "BUE",
        "to": "GRU",
        "departure_time": "2026-09-12 09:00",
        "arrival_time": "2026-09-12 11:00"
      },
      {
        "flight_number": "IB201",
        "from": "GRU",
        "to": "MAD",
        "departure_time": "2026-09-12 13:00",
        "arrival_time": "2026-09-12 23:00"
      }
    ]
  }
]
```

## Running Tests

Unit tests for the journey search service are in `tests/services/`; API integration tests are in `tests/api/`. Install runtime and dev dependencies and run tests:

```bash
  pip install -r requirements.txt -r requirements-dev.txt
  pytest tests/ -v
```

Optional: run with coverage:

```bash
  pytest tests/ -v --cov=app --cov-report=term-missing
```

### Running tests with Docker (optional)

To run tests inside a container:

```bash
    docker run --rm \
      -v "$PWD":/app \
      -w /app \
      flight-journey-api \
      sh -c "pip install -r requirements-dev.txt && pytest -v"
```

## Notes & Intentional Trade-offs / Future Improvements

The following items were intentionally left out to keep the solution focused on the challenge scope, but would be the next steps in a production system:

- **External API Integration**: Replace the in-memory `get_flight_events` provider with an HTTP client that calls a real Flight Events API endpoint.
- **Database Integration**: Add persistence layer to cache flight events or store search results.
- **Extended Journey Support**: Extend the service to support journeys with more than 2 flight segments.
- **Performance Optimizations**: Implement caching for frequently searched routes or dates, and optimize the search algorithm for large event sets.
- **Additional Validation**: Add validation for city code formats (IATA) and date ranges.

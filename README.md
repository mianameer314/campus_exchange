# Campus Exchange API

A complete backend platform for a university secondhand marketplace
built with FastAPI.

## Features

-   User Authentication and JWT-based login/signup
-   Email OTP verification and ID upload with admin approval
-   Listings management: create, update, delete, view, and search
    listings
-   Search listings by query, category, price range, university, and
    sorting
-   Favorites management for users
-   Notifications for actions and updates
-   Admin panel to manage users and verifications
-   AI-powered price predictions and duplicate checks
-   Real-time chat functionality via WebSocket with:
    -   Typing indicators
    -   Delivery receipts
    -   Editable and deletable messages
    -   User blocking support to prevent unwanted communication
-   Secure password hashing and role-based access control
-   File upload and management for images and ID documents
-   Database migrations with Alembic and PostgreSQL integration
-   Interactive API docs with Swagger UI and ReDoc
-   Health check endpoint

## Development Progress by Days

### Day 1: Initial Setup and Models

-   Set up FastAPI project structure with modular API routers.
-   Defined core SQLAlchemy ORM models, including the `Listing` model
    with fields like `title`, `description`, `category`, `price`,
    `owner_id`, and timestamps.
-   Established PostgreSQL database connection and session management
    with `sqlalchemy` and Alembic migrations.

### Day 2: Enhancements to Listings Model

-   Added support for images (stored as JSON array of URLs), listing
    status (`ACTIVE`, `SOLD`, `ARCHIVED`), and `updated_at` timestamp to
    listings.
-   Implemented Alembic migration to add these new columns with
    safeguards to avoid duplication.
-   Indexed listing status for efficient filtering queries.

### Day 3: Full-Text Search with PostgreSQL

-   Integrated PostgreSQL full-text search functionality by adding a
    `search_vector` column of type TSVECTOR to the `listings` table.
-   Wrote Alembic migration to add `search_vector` column, create a GIN
    index on it, implemented trigger function and trigger to auto-update
    the vector on INSERT and UPDATE.
-   Updated SQLAlchemy `Listing` model to include deferred loading of
    the `search_vector` column for efficient search queries.

### Day 4: Search & Filter API Endpoint and Project Modularization

-   Developed a robust search API endpoint supporting:
    -   Full-text search on listing titles and descriptions using
        PostgreSQL TSVECTOR
    -   Filtering by category, price range, and university
    -   Sorting by various fields like creation date or price, with
        ascending/descending options
    -   Pagination with configurable page number and page size
-   Refactored project structure into clearly separated folders `crud/`
    (database operations), `services/` (business logic), and `api/`
    (HTTP endpoints).
-   Enhanced maintainability by isolating responsibilities and
    simplifying import paths.
-   Added comprehensive validation and error handling for API query
    parameters.

### Day 5: Real-Time Chat with WebSocket

-   Implemented real-time chat system via WebSocket connections for
    direct user-to-user messaging about listings.
-   Features added:
    -   Typing indicators to show when a user is typing
    -   Delivery receipts to confirm message delivery
    -   Message editing and deleting with proper permission checks
    -   User blocking to prevent receiving messages from blocked users
-   Ensured JWT-based authentication on WebSocket handshake for secure
    user identification.
-   Added active connection management to support multiple concurrent
    WebSocket clients.
-   Provided sanitization for message content to prevent injection
    attacks.
-   Enhanced error handling and logging for stable real-time
    communication.
-   Completed Alembic migrations for adding `edited` and `deleted` flags
    to chat messages and created new `blocked_users` table.

## Prerequisites

-   Docker & Docker Compose (recommended)
-   Python 3.8+
-   PostgreSQL database (or use Dockerized Postgres)
-   Git (to clone the repo)

## Full Setup & Installation Guide

### 1. Clone the Repository

``` bash
git clone https://github.com/mianameer314/campus_exchange.git
cd campus_exchange
```

### 2. Environment Setup

Copy example environment variables and update them with your values:

``` bash
cp .env.example .env
```

Edit `.env` and set:

-   `SQLALCHEMY_DATABASE_URI` (e.g.,
    `postgresql://username:password@localhost:5432/dbname`)
-   `ADMIN_EMAIL` and `ADMIN_PASSWORD`
-   `JWT_SECRET` for token signing (used in authentication and
    WebSocket)
-   Other optional environment variables as needed

### 3. Docker (Recommended)

To build and run the app with Docker:

``` bash
docker-compose up --build
```

This builds containers for FastAPI and PostgreSQL, applies migrations,
and exposes the app at `http://localhost:8000`

### 4. Running Locally Without Docker

#### a. Create & activate virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scriptsctivate
```

#### b. Install dependencies

``` bash
pip install -r requirements.txt
```

#### c. Run database migrations

Make sure PostgreSQL is running and accessible via connection URL, then:

``` bash
alembic upgrade head
```

#### d. Start FastAPI app with live reload

``` bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation available at:

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## Example Search API Usage

``` bash
curl "http://localhost:8000/api/v1/listings/search?q=book&category=Books&min_price=0&max_price=1000&university=Attock&sort_by=created_at&sort_order=desc&page=1&page_size=10"
```

Supports:

-   Keyword search (`q`)
-   Filters: `category`, `min_price`, `max_price`, `university`
-   Sorting: `sort_by` (e.g., `created_at`), `sort_order` (`asc` or
    `desc`)
-   Pagination: `page`, `page_size`

## Project Structure

-   `app/main.py`: Application entry, router registrations
-   `app/api/v1/`: API route modules (auth, listings, search, etc.)
-   `app/crud/`: Database CRUD operations
-   `app/models/`: SQLAlchemy ORM models
-   `app/schemas/`: Pydantic request and response schemas
-   `app/services/`: Business and search logic
-   `app/db/`: Database session and engine configuration
-   `alembic/`: Database migration scripts

## Tips & Notes

-   Always get DB session via `get_db` dependency to avoid connection
    issues.
-   Clear FastAPI OpenAPI schema cache after changing
    dependencies/routes by setting `app.openapi_schema = None`.
-   Ensure route ordering to prevent conflicts, e.g., `/listings/search`
    before `/listings/{listing_id}`.
-   Frontend should present search/filter parameters in user-friendly
    dropdowns, text inputs, and sliders as appropriate.
-   Project is modularized extensively to support maintainability and
    future enhancements.
-   Use JWT token passed in WebSocket `Authorization` header for secure
    real-time chat.

## License

MIT License

## Contact

For questions, issues, or contributions, please open a GitHub issue or
submit a pull request.

Thank you for using Campus Exchange API!

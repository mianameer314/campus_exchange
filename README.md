# Campus Exchange API

A complete backend platform for a university secondhand marketplace built with FastAPI.

---

## Features

- User Authentication and JWT-based login/signup
- Email OTP verification and ID upload with admin approval
- Listings management: create, update, delete, view, and search listings
- Search listings by query, category, price range
- Favorites management for users
- Notifications for actions and updates
- Admin panel to manage users and verifications
- AI-powered price predictions and duplicate checks
- Real-time chat functionality via WebSocket
- Secure password hashing and role-based access control
- File upload and management for images and ID documents
- Database migrations with Alembic and PostgreSQL integration
- Interactive API docs with Swagger UI and ReDoc
- Health check endpoint

---

## Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.8+
- PostgreSQL database (or use Dockerized Postgres)
- Git (to clone the repo)

---

## Full Setup & Installation Guide

### 1. Clone the Repository

```

git clone https://github.com/mianameer314/campus_exchange.git
cd campus_exchange

```

### 2. Environment Setup

Copy the example environment variables and update them with your own values:

```

cp .env.example .env

```

Edit `.env` and set the following variables:

- `SQLALCHEMY_DATABASE_URI` (e.g., `postgresql://username:password@localhost:5432/dbname`)
- `ADMIN_EMAIL` (your admin email)
- `ADMIN_PASSWORD` (your admin password)
- Other optional settings can be adjusted as needed

### 3. Docker (Recommended)

If you have Docker installed, you can build and run the app quickly:

```

docker-compose up --build

```

This will:

- Build the FastAPI backend container
- Start a PostgreSQL database container
- Run migrations automatically
- Make the app available on `http://localhost:8000`

You can stop docker with `Ctrl+C` or:

```

docker-compose down

```

### 4. Running Locally without Docker

If you want to run the app without Docker:

#### a. Create and activate a virtual environment

```

python3 -m venv .venv
source .venv/bin/activate   \# On Windows: .venv\Scripts\activate

```

#### b. Install dependencies

```

pip install -r requirements.txt

```

#### c. Run database migrations

Make sure your Postgres database is running and accessible via the connection string in `.env`.

Run migrations with Alembic:

```

alembic upgrade head

```

#### d. Start the FastAPI app with live reload

```

uvicorn app.main:app --reload

```

Your app will be accessible at: `http://localhost:8000`

### 5. API Documentation

Access interactive documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 6. Testing the API

Use the Swagger UI to test endpoints or tools like Postman or curl.

Example curl to test search:

```

curl "http://localhost:8000/api/v1/search?q=book\&category=Books"

```

---

## Key Project Structure Overview

- `app/main.py`: App startup, router inclusions, middleware, OpenAPI settings
- `app/api/v1/`: Modular API routers for auth, listings, search, verification, admin, AI, chat, etc.
- `app/db/session.py`: Database engine and sessionmaker configuration with dependency wrapper
- `app/models/`: SQLAlchemy ORM models representing DB tables
- `app/schemas/`: Pydantic models for data validation and serialization
- `app/core/`: Core configuration, security utilities, hashing and token management
- `alembic/`: Database migrations management

---

## Important Notes

### Using DB Session Dependency Correctly

Always use the provided `get_db` dependency function to get a SQLAlchemy session:

```

from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()

# In route:

def endpoint(db: Session = Depends(get_db)):
\# use db here

```

**Do NOT use `Depends(SessionLocal)` directly!**  
This causes problems like the `local_kw` required query parameter error.

### Clearing OpenAPI Schema Cache

If you change route parameters or dependency signatures, clear FastAPI’s OpenAPI schema cache by adding:

```

app.openapi_schema = None

```

and restarting to refresh the docs.

---

## Deployment Recommendations

- For production, consider using process managers like Gunicorn with Uvicorn workers.
- Use environment variables and secret management systems.
- Set up HTTPS and CORS policies.
- Clear build caches on deployment platforms to avoid stale API docs issues.
- Automate migrations during deployment.

---

## Contributing

Feel free to fork, create branches for features/bugs, and make pull requests.  
Please keep consistent code style and add tests for new features.

---

## License

MIT License

---

## Contact

For questions, open an issue on GitHub or contact the maintainer.

Thank you for using Campus Exchange API!
```


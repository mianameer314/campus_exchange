# University Secondhand Marketplace — Day1+Day2 Backend

## Quickstart (Docker)
1. Copy `.env.example` to `.env` and edit values (DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD).
2. Run: `docker-compose up --build`
3. Open docs: http://localhost:8000/docs

## What's included
- Auth: signup/login/me (JWT)
- Verification: OTP email, upload ID, admin approve/reject
- Listings, Search, Favorites, Notifications, Admin, Chat (WS), AI price-suggest
- Alembic migrations included
- Uploads saved to ./uploads/ids

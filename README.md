# SnapURL — URL Shortener with Analytics

A full-stack, high-scale URL shortening platform built with FastAPI, PostgreSQL, Redis, and Next.js. Supports custom aliases, TTL-based expiration, click analytics, Redis caching, and API rate limiting.

## Live Demo

- **Frontend:** https://snapurl-url-shortener.vercel.app
- **Backend API:** https://snapurl-url-shortener-1.onrender.com/docs

> Render free tier spins down after 15 minutes of inactivity. The first request after a period of inactivity may take ~30 seconds to wake the service.

[![Tests](https://img.shields.io/badge/tests-7%20passing-brightgreen)](#testing)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688)](https://fastapi.tiangolo.com/)

---

## Features

- **URL shortening** with randomly generated short codes
- **Custom aliases** — e.g. `/my-portfolio`
- **TTL expiration** — links expire after N days
- **Click analytics** — click count and IP address per link
- **Redis Caching** — 99% of redirects are served from memory, taking microseconds instead of milliseconds
- **Rate Limiting** — Protected against spam (max 5 new links per minute per IP)
- **REST API** with Swagger docs
- **7 pytest tests** including a concurrency test

---

## Tech Stack

**Backend**
- FastAPI — async API framework
- PostgreSQL — production database (Supabase)
- Redis — in-memory cache for high-speed redirects
- SQLAlchemy — ORM
- Alembic — schema migrations

**Frontend**
- Next.js (React)
- Tailwind CSS

**Deployment**
- Frontend: Vercel
- Backend: Render
- Database: Supabase (PostgreSQL)

**Testing**
- pytest — 7 tests

---

## Notable Engineering

### 1. Race Condition 1: Short Code Collision
Original code checked if a short code existed, then inserted it — a TOCTOU (time-of-check to time-of-use) window. Two simultaneous requests could both check for a code, both see it as free, and both try to insert it.
**Fix:** Rely on the database `UNIQUE` constraint and catch `IntegrityError`. The insert is atomic.

### 2. Race Condition 2: Lost Update on Click Counter
Original code read the click count, incremented it in Python, then wrote it back. Under concurrent clicks, some increments were lost.
**Fix:** Use an atomic SQL `UPDATE urls SET clicks = clicks + 1`. Verified with a test that spawns 20 concurrent sessions and asserts the final count is exactly 20.

### 3. High-Scale Read Caching with Redis
To prevent the database from crashing under heavy read load, Redis was introduced. When a redirect is requested, the API first checks Redis.
- **Cache Hit:** Instant redirect (no database read).
- **Cache Miss:** Fetches from PostgreSQL, saves to Redis (TTL 1 hour), then redirects.

### 4. API Rate Limiting
Implemented a Token Bucket rate limiter using `fastapi-limiter` to restrict the `/shorten` endpoint to 5 requests per minute per IP, preventing DDoS attacks and spam.

---

## Project Structure

```text
snapurl-url-shortener/
├── backend/
│   ├── alembic.ini
│   ├── migrations/
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── tests/
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       ├── database.py
│       └── routes/
│           └── shortener.py
├── frontend/
│   ├── app/
│   ├── public/
│   └── package.json
└── README.md
```

---

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

Create `.env` with:

```text
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/snapurl_dev
TEST_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/snapurl_test
BASE_URL=http://localhost:8000
```

Apply migrations:

```bash
alembic upgrade head
```

Start Redis (Required for caching):
```bash
redis-server
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

---

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

Expected: `7 passed`.

Test coverage:

| Test | What it verifies |
|---|---|
| `test_shorten_creates_url` | Basic shortening works |
| `test_custom_code` | Custom aliases work |
| `test_duplicate_custom_code_rejected` | Duplicate codes rejected |
| `test_redirect_increments_clicks` | Click counting works |
| `test_concurrent_increments_are_atomic` | **20 concurrent increments → count is exactly 20** |
| `test_unknown_code_returns_404` | Unknown codes return 404 |
| `test_expired_link_returns_410` | Expired links return 410 Gone |

---

## API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/shorten` | Create a short URL (Rate limited: 5/min) |
| `GET` | `/{short_code}` | Redirect to original URL (Redis Cached) |
| `GET` | `/stats/{short_code}` | Get click stats |

---

## Future Improvements

- User authentication with JWT
- Custom domain support
- QR code generation
- Advanced analytics (device, location, browser)
- Link management dashboard

---

## License

MIT
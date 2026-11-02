# TenMission

Inventory booking system with FastAPI backend + React frontend, Supabase PostgreSQL, JWT auth, and CSV ingestion logic.

---

## Quick Links

- [Setup Guide](SETUP.md) — Fresh clone to running app
- [API Docs](http://localhost:8000/docs) — Interactive API docs (when running)

---

## Project Structure

```
codebase/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM
│   │   ├── schemas/         # Pydantic contracts
│   │   ├── crud/            # Database operations
│   │   ├── services/        # Business logic
│   │   ├── routers/         # API endpoints
│   │   └── core/            # Config, auth, exceptions
│   ├── data/                # CSV source files (inventory.csv, members.csv)
│   ├── scripts/
│   │   ├── ingest.py        # Registry-based CSV ingestion
│   │   ├── cleanup_db.py    # Database cleanup
│   │   └── test_api_flow.py # Full API flow test
│   ├── alembic/             # Migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI
│   │   ├── pages/           # Route components
│   │   ├── context/         # React context
│   │   └── api/             # API client
│   └── package.json
└── package.json             # Root orchestrator
```

---

## Key Features

| Feature           | Implementation                                                             |
| ----------------- | -------------------------------------------------------------------------- |
| **Auth**          | JWT (access/refresh tokens)                                                |
| **Booking Limit** | MAX_BOOKINGS=2 per member, enforced with `SELECT FOR UPDATE`               |
| **Inventory**     | `is_active` flag (auto-set from expiration), Title Case titles             |
| **CSV Ingestion** | Plain-function ingestion, batched native upsert, per-row errors, CSV dedup |
| **API Errors**    | Specific HTTP codes: 400, 404, 409, 422                                    |

---

## Development Commands

```bash
# Full fresh setup (after configuring .env)
npm run install:all
npm run db:migrate
npm run db:ingest
npm run dev

# Daily development
npm run dev                    # Start both servers
npm run dev:backend            # Backend only
npm run dev:frontend           # Frontend only

# Database
npm run db:migrate             # Run migrations
npm run db:ingest              # Re-run ingestion (safe, idempotent)
npm run db:reset               # Full reset: downgrade + migrate + ingest

```

---

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic v2
- **Frontend**: React 18, Vite, Tailwind CSS, React Router
- **Database**: Supabase (PostgreSQL)
- **Auth**: JWT (HS256)

---

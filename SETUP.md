# TenMission - Fresh Setup Guide

Complete step-by-step instructions to run the TenMission application from a fresh clone.

---

## Prerequisites

| Tool                 | Version | Install Command                                           |
| -------------------- | ------- | --------------------------------------------------------- |
| **Python**           | 3.11+   | `brew install python@3.11` / `asdf install python 3.11.9` |
| **Node.js**          | 20+     | `brew install node@20` / `asdf install nodejs 20.15.0`    |
| **npm**              | 10+     | Included with Node.js                                     |
| **Supabase Account** | -       | [supabase.com](https://supabase.com)                      |

---

## 1. Clone & Configure

```bash
# Navigate to project root
cd /path/to/codebase

# Copy environment template
cp backend/.env.example backend/.env
```

### Edit `backend/.env` with your Supabase credentials:

```bash
# Required: Get from Supabase Dashboard → Settings → Database → Connection String
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres

# JWT Settings (generate a secure secret for production)
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Booking Limits
MAX_BOOKINGS=2

# CORS (frontend dev server)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

> **Important**: Use the `postgresql+asyncpg://` prefix for async SQLAlchemy. Get the connection string from Supabase → Settings → Database → Connection string → URI format.
>
> **Note**: `.env` is not tracked in git. Copy from `.env.example` and fill in your own values.

---

## 2. Install Dependencies

### Option A: Automated (recommended)

```bash
npm run install:all
```

### Option B: Manual

```bash
# Root dependencies (concurrently)
npm install

# Backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

---

## 3. Run Database Migrations

```bash
# From project root
npm run db:migrate
```

**Expected output:**

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial
```

This creates 3 tables in your Supabase database:

- `inventory`
- `members`
- `bookings`

**Verify in Supabase Dashboard:**
Go to Table Editor → confirm all 4 tables exist with correct columns.

---

## 4. Run Data Ingestion (Idempotent)

```bash
# From project root
npm run db:ingest
```

## 5. Start Development Servers

```bash
# From project root - starts BOTH servers
npm run dev
```

### Access Points

| Service         | URL                        | Notes                |
| --------------- | -------------------------- | -------------------- |
| **Frontend**    | http://localhost:5173      | Main application     |
| **Backend API** | http://localhost:8000      | JSON API             |
| **API Docs**    | http://localhost:8000/docs | Interactive API docs |

---

## 6. Verify End-to-End

### Test Login

1. Open http://localhost:5173
2. Enter any valid email (e.g., `test@example.com`)
3. Click "Sign In" → redirects to Action page

### Test Member Selector

1. Dropdown at top shows 46 members (from CSV)
2. Select a member → name appears in header

### Test Inventory Booking

1. Click "Browse & Book Inventory"
2. Search works in real-time (title/description)
3. Cards show: title, description, available count, expiration
4. Quantity selector capped at `min(remaining, 2 - member_bookings)`
5. Click "Book" → success toast, booking reference generated

### Test Booking Management

1. Go to Action page → "Manage Existing Bookings"
2. Shows active bookings for selected member
3. Click "Cancel" → restores inventory count, decrements member booking_count

---

## Troubleshooting

### Migration Fails

```bash
# Check DATABASE_URL format
cat backend/.env | grep DATABASE_URL

# Should be: postgresql+asyncpg://user:pass@host:5432/dbname
# NOT: postgres://user:pass@host:5432/dbname
```

### Ingestion Errors

```bash
# Run with verbose output
cd backend
python scripts/ingest.py

# Common issues:
# - CSV files not in backend/data/ directory
# - Date format mismatch (inventory uses DD/MM/YYYY)
# - Required columns missing from CSV headers
```

### Port Conflicts

```bash
# Backend (8000) or Frontend (5173) in use?
lsof -i :8000
lsof -i :5173

# Kill and restart
kill -9 <PID>
npm run dev
```

## Quick Command Reference

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

---

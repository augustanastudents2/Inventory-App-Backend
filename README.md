# ASA Inventory App Backend (FastAPI + Supabase)

Backend API for the **ASA Inventory Management System**. Built with **FastAPI** and **Supabase** (Postgres + Auth). Designed for deployment on Render and consumed by the Vue Inventory frontend.

## What this API does

- **Products**: CRUD + stock adjustments
- **Stock history**: records stock change events per product and returns `stockHistory` for charts
- **Settings**: categories, tags, vendors, storage locations
- **Users**: create users (Supabase Auth + `users` table), update roles, delete users (deletes from Auth + table)
- **Auth**: login via Supabase Auth

## Tech stack

- **FastAPI** + **Uvicorn**
- **Supabase** (`supabase-py`)
- **Pydantic v2** (`pydantic-settings`)

## Local development

### 1) Create a virtualenv (recommended)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Environment variables

Create a `.env` in the project root (do **not** commit it).

```env
# Supabase
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<anon-public-key>
SUPABASE_SERVICE_KEY=<service-role-key>

# Optional: comma-separated list of allowed frontend origins
# CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

### 3) Database schema

Run the SQL in:

- `database/database_schema.sql`

in your Supabase project **SQL Editor**.

### 4) Run the API

```bash
uvicorn main:app --reload
```

Open:
- **Docs**: `http://127.0.0.1:8000/docs`
- **Health**: `http://127.0.0.1:8000/api/health`

## API paths (high-level)

Base path: `/api`

### Auth (`/api/auth`)
- `POST /login`

### Users (`/api/users`)
- `GET /`
- `POST /` (creates Supabase Auth user + inserts `users` table)
- `PATCH /{user_id}/role`
- `DELETE /{user_id}` (deletes from Supabase Auth + `users` table)

### Products (`/api/products`)
- `GET /`
- `GET /{product_id}`
- `POST /`
- `PUT /{product_id}`
- `POST /adjust-stock`
- `DELETE /{product_id}`

### Settings (`/api/settings`)
- `GET/POST/PATCH/DELETE` categories, tags, vendors
- `GET/POST/PATCH/DELETE` storage locations

## Deployment (Render)

- **Build command**: `pip install -r requirements.txt`
- **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Required env vars**: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`, optionally `CORS_ORIGINS`

## Scheduled Supabase keepalive (GitHub Actions)

This repo includes:

- `.github/workflows/supabase-keepalive.yml`

Add these GitHub Secrets in the repo:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_KEEPALIVE_PATH` (example: `products?select=id&limit=1`)

## Repo setup checklist

### Supabase

- [ ] Create a Supabase project
- [ ] Run `database/database_schema.sql` in Supabase **SQL Editor**
- [ ] Confirm tables exist: `products`, `stock_history`, `categories`, `tags`, `vendors`, `storage_locations`, `users`

### Local dev

- [ ] Create `.env` with `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY` (and optional `CORS_ORIGINS`)
- [ ] Create/activate venv and `pip install -r requirements.txt`
- [ ] Start: `uvicorn main:app --reload`
- [ ] Smoke test: open `http://127.0.0.1:8000/api/health`

### Render (deployment)

- [ ] Set Render env vars: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY` (and `CORS_ORIGINS` if needed)
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Smoke test: `GET https://<render-host>/api/health`

### GitHub Actions (Supabase keepalive)

- [ ] Add repo secrets: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_KEEPALIVE_PATH`
- [ ] Run once manually from the GitHub Actions UI to verify it returns 200

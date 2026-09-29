# Deployment Guide

This is kept separate from local development instructions (see the main README) since
production needs differ: a real database, secrets management, and persistent file storage.

## Option A — Docker Compose (simplest, single machine / VPS)

```bash
# From the project root
cp backend/.env.example backend/.env      # fill in OPENAI_API_KEY if you want AI chat/insights
export OPENAI_API_KEY=sk-...              # or export it in your shell / CI secret store
docker compose up --build
```
- Backend: `http://<host>:8000`
- Frontend: `http://<host>:5173`

This setup still uses SQLite (stored in a Docker volume) and local disk for uploads/models/reports —
fine for a single-instance deployment or staging.

## Option B — Separate hosted backend + static frontend (recommended for production)

### Backend
Deploy `backend/` to any host that runs an ASGI app (Render, Railway, Fly.io, a VPS with
`uvicorn`/`gunicorn` behind nginx). Steps are the same everywhere:

1. Set environment variables on the host:
   - `DATABASE_URL` → a managed PostgreSQL connection string (e.g. `postgresql://user:pass@host:5432/dbname`)
     — no code changes needed, SQLAlchemy handles both.
   - `OPENAI_API_KEY` → your key, set as a secret, never committed
   - `FRONTEND_ORIGIN` → your deployed frontend's URL (for CORS)
   - `MAX_UPLOAD_SIZE_MB` → adjust if needed
2. Point `UPLOAD_DIR`, `PROCESSED_DIR`, `MODELS_DIR`, `REPORTS_DIR` at a persistent volume or
   mounted object storage if your host has an ephemeral filesystem (most PaaS hosts do).
3. Install `requirements.txt` and run: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. `psycopg2-binary` is required in addition to `requirements.txt` if you use PostgreSQL —
   add it to `requirements.txt` before deploying.

### Frontend
1. Set `VITE_API_BASE_URL` to your deployed backend's URL, e.g. `https://api.yourdomain.com/api`
   (copy `.env.example` to `.env.production` and set it there).
2. `npm run build` — produces a static `dist/` folder.
3. Deploy `dist/` to Vercel, Netlify, Cloudflare Pages, or any static host / CDN.

## Database migration note

This project creates tables automatically at startup (`init_db()` calls `Base.metadata.create_all`).
For production with schema changes over time, introduce Alembic migrations rather than relying on
`create_all`, which does not handle altering existing tables.

## Security checklist before going live

- [ ] `OPENAI_API_KEY` set only via host secrets, never in a committed `.env`
- [ ] `FRONTEND_ORIGIN` restricted to your real frontend domain (not `*`)
- [ ] `MAX_UPLOAD_SIZE_MB` set to a sane limit for your expected traffic
- [ ] Persistent storage configured for uploads/models/reports (not ephemeral container disk)
- [ ] HTTPS termination in front of both services (most PaaS hosts do this automatically)

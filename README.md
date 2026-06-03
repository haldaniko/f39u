# AI-Powered News Portal (Facts 39 Unlimited)

Production-oriented full-stack news portal with automated aggregation, AI rewriting, moderation workflow, analytics, and a premium React frontend.

## Stack

- Backend: Python 3.12, Django 5, DRF, JWT, Celery, Redis, PostgreSQL, drf-spectacular
- Frontend: React 19, Vite, React Router, Axios, TailwindCSS, Framer Motion, React Query
- Infra: Docker, Docker Compose, Nginx, Gunicorn, .env configuration

## Project Structure

- backend/: Django API, admin panel, Celery tasks, providers, AI rewriting, analytics
- frontend/: React news portal UI
- infra/nginx/: Nginx reverse proxy for production
- docker-compose.yml: Development stack
- docker-compose.prod.yml: Production stack
- .env.example: Environment template

## Core Workflow

1. Fetch article from enabled providers.
2. Store and publish original article as a duplicated news entry.
3. Optionally rewrite with selected AI provider for editorial workflows.

## Backend Apps

- apps/news:
  - Models: Article, Category, Tag, Source
  - Provider abstraction (`NewsProvider`) with NewsAPI, GNews, Guardian, RSS adapters
  - Service and repository layers for ingestion/query/cleanup
  - Endpoints:
    - `/api/news/`
    - `/api/news/{slug}/`
    - `/api/categories/`
    - `/api/tags/`
    - `/api/search/`
    - `/api/trending/`
- apps/ai:
  - AI settings model
  - `AIRewriter` abstraction with env-selected provider
  - Rewrite service generating title, summary, body, SEO description, tags
- apps/users:
  - JWT auth endpoints:
    - `/api/auth/login/`
    - `/api/auth/refresh/`
    - `/api/auth/me/`
- apps/analytics:
  - Daily analytics reports
  - Admin stats endpoint:
    - `/api/admin/statistics/`

## Scheduled Jobs (Celery)

- Every 15 min: `fetch_latest_news_task`
- Every 15 min: `rewrite_pending_articles_task`
- Daily: `cleanup_duplicates_task`
- Daily: `generate_daily_report_task`

## Security

- DRF rate limiting for anon/authenticated users
- CSRF middleware enabled
- CORS and CSRF trusted origins via env
- Secure cookie defaults in non-debug mode
- Security headers (XSS/content type/frame options)

## API Documentation

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

## Quick Start (Docker Dev)

1. Copy env template:
   - `cp .env.example .env`
2. Fill API keys and secrets.
3. Start:
   - `docker compose up --build`
   - Dev startup fetches external news and publishes them to the site.
4. Services:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000/api`
   - Admin: `http://localhost:8000/admin`

## Production Start

1. Configure `.env` for production secrets and domains.
2. Run:
   - `docker compose -f docker-compose.prod.yml up --build -d`
3. Access app through Nginx at port `80`.

## Local Non-Docker Setup

### Backend

1. Create venv and install dependencies from `backend/requirements/dev.txt`.
2. Configure `.env`.
3. Run migrations:
   - `python manage.py migrate`
4. Start API:
   - `python manage.py runserver`
5. Start Celery worker and beat:
   - `celery -A config worker -l info`
   - `celery -A config beat -l info`

### Frontend

1. Install deps:
   - `npm install`
2. Run dev server:
   - `npm run dev`

## Testing

- Backend unit/integration tests:
  - `python manage.py test`

## Notes

- AI provider implementations currently expose abstraction and fallback rewrite behavior. Plug in SDK-specific calls in `backend/apps/ai/providers.py` for production provider APIs.
- RSS adapter interface exists and can be extended with feedparser-based ingestion.

## External Ingestion

- Manual fetch command:
   - `python manage.py fetch_external_news`
- On container startup, backend automatically runs `fetch_external_news` once.

## Current News Sources Behavior

- The ingestion service calls providers in `backend/apps/news/providers.py`:
   - NewsAPI (`NEWSAPI_KEY`)
   - GNews (`GNEWS_API_KEY`)
   - The Guardian (`GUARDIAN_API_KEY`)
   - RSS provider (works with no API key)
- If keys are empty, those providers return no articles.
- RSS auto-loads from default public feeds even when all API keys are empty.
- You can override feed list with `RSS_FEEDS` in `.env` (comma-separated URLs).
- For AI rewriting, all provider classes currently inherit a fallback implementation, so rewriting still works without external LLM APIs.

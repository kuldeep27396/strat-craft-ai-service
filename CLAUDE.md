# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StratCraft AI is a monorepo SaaS platform that generates customized marketing strategies using AI agents. It combines business intelligence with client objectives to automate proposal creation.

**Architecture**: FastAPI backend + Next.js 14 frontend + PostgreSQL + LangGraph AI agents

## Development Commands

### Backend (Python/FastAPI)

```bash
cd backend

# Initial setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure environment variables

# Database migrations
alembic upgrade head      # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration

# Development server
uvicorn app.main:app --reload  # Runs on http://localhost:8000
```

### Frontend (Next.js)

```bash
cd frontend

# Initial setup
npm install
cp .env.local.example .env.local  # Configure API URL

# Development
npm run dev        # Runs on http://localhost:3000
npm run build      # Production build
npm run start      # Run production build
npm run lint       # Run ESLint
```

### Docker Services (Optional)

```bash
docker-compose up -d  # Start PostgreSQL (5432) and Redis (6379)
docker-compose down   # Stop services
```

## Architecture

### Backend Structure

- **`app/main.py`**: FastAPI application entry point, includes all API routers
- **`app/config.py`**: Pydantic Settings for environment configuration
- **`app/database.py`**: SQLAlchemy engine and session management
- **`app/api/`**: API route modules organized by domain
  - `auth.py` - Authentication endpoints (login, register, token refresh)
  - `profiles.py` - Business profile CRUD
  - `questionnaires.py` - Client questionnaire management
  - `strategies.py` - AI strategy generation and retrieval
- **`app/models/`**: SQLAlchemy ORM models (all use UUID primary keys)
- **`app/schemas/`**: Pydantic schemas for request/response validation
- **`app/agents/`**: LangGraph AI agent orchestrators (currently placeholder)

### Frontend Structure

- **`src/app/`**: Next.js 14 App Router pages
  - `dashboard/` - Main application pages (profiles, questionnaires, strategies)
- **`src/components/`**: Reusable UI components (Radix UI + TailwindCSS)
- **`src/lib/`**: API client functions
- **`src/types/`**: TypeScript type definitions

### Key Technologies

- **State Management**: Zustand (client) + React Query (server state)
- **Forms**: React Hook Form + Zod validation
- **UI**: shadcn/ui patterns with Radix UI primitives
- **Database**: PostgreSQL with connection pooling (10 base, 20 max overflow)

### Agent Workflow (Planned)

The LangGraph orchestrator follows this flow:
1. Context Builder → SEO Strategy → Content Strategy
2. Quality Check → (if fails) Refinement Agent → retry
3. Approved → Output strategy

## API Routes

- `GET/POST /api/auth` - Authentication
- `GET/POST /api/profiles` - Business profiles
- `GET/POST /api/questionnaires` - Client questionnaires
- `GET/POST /api/strategies` - Generated strategies
- `GET /docs` - Auto-generated FastAPI docs (Swagger UI)

## Environment Variables (Backend)

Required in `backend/.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `OPENAI_API_KEY` - Required for AI agents

Optional:
- `ANTHROPIC_API_KEY` - Alternative LLM provider
- `PINECONE_API_KEY` - Vector database for knowledge base
- `REDIS_URL` - Caching and Celery broker

## Database Migrations

Use Alembic for schema changes:
1. Modify models in `backend/app/models/`
2. Run `alembic revision --autogenerate -m "description"`
3. Review generated migration in `backend/alembic/versions/`
4. Apply with `alembic upgrade head`

## Current State

**Implemented**: Business profiles, client questionnaires, basic auth, dashboard UI
**Placeholder**: AI agent implementation (returns mock data)
**Not Implemented**: Testing framework, CI/CD, PDF export, real-time collaboration

## Conventional Commits

The project uses conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring

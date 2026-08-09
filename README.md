# Belskap

FastAPI backend for Belskap. The first API supports creating an account with an
email and password. Passwords are stored as Argon2 hashes, never as plain text.

## Project structure

```text
belskap/
├── backend/       FastAPI application, migrations, and tests
├── frontend/      Next.js authentication UI and dashboard
└── compose.yaml   Runs the project's containerized services
```

## Run with Docker

Docker Compose starts both the API and PostgreSQL, applies database migrations,
and persists PostgreSQL data in a named volume:

```powershell
docker compose up --build
```

Open the frontend at <http://localhost:3000> or the interactive API docs at
<http://localhost:8000/docs>.

## Register an account

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/v1/auth/register `
  -ContentType "application/json" `
  -Body '{"email":"user@example.com","password":"a-secure-password"}'
```

The endpoint returns the user's ID, normalized email, and creation date. A
duplicate email returns HTTP 409 and invalid input returns HTTP 422.

## Run locally without Docker

Create a PostgreSQL database, copy `.env.example` to `.env`, then install and run:

```powershell
cd backend
Copy-Item .env.example .env
pip install -e ".[dev]"
alembic upgrade head
python main.py
```

From the `backend` directory, run tests with `pytest`.

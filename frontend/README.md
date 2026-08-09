# Belskap frontend

Next.js frontend for account creation, login, and the authenticated dashboard.

For normal local development, start the full stack from the repository root:

```powershell
docker compose up --build
```

The frontend is available at <http://localhost:3000>. Inside Docker, its server
connects to FastAPI using `BACKEND_URL=http://api:8000`. Authentication tokens
are kept in an HTTP-only cookie and are not exposed to browser JavaScript.

To work on only the frontend, copy `.env.example` to `.env.local`, then run:

```powershell
pnpm install
pnpm dev
```

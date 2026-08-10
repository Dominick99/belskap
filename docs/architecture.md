# Belskap architecture

Belskap runs as three containers: a Next.js frontend, a FastAPI backend, and a
PostgreSQL database.

```mermaid
flowchart LR
    User([Web browser])
    Frontend["Frontend container<br/>Next.js<br/>Port 3000"]
    Backend["Backend container<br/>FastAPI<br/>Port 8000"]
    Database[("Database container<br/>PostgreSQL<br/>Port 5432")]

    User -->|"GET pages<br/>POST login, signup, and logout"| Frontend
    Frontend -->|"POST /api/v1/auth/register<br/>POST /api/v1/auth/login<br/>GET /api/v1/auth/me"| Backend
    Backend -->|"SQL SELECT and INSERT"| Database
    Database -->|"Users and query results"| Backend
    Backend -->|"JSON responses"| Frontend
    Frontend -->|"HTML and HTTP-only session cookie"| User
```

The frontend serves the interface and manages the user's session cookie. It
sends registration, login, and current-user API requests to the backend. The
backend validates those requests, handles passwords and authentication tokens,
and reads or writes user records in PostgreSQL.

Docker Compose connects the containers on an internal network. Users open the
frontend at `localhost:3000`; the backend is also available at `localhost:8000`
for API access and interactive documentation.

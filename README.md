# Ottoke - Rate My Suffering

A full-stack web application where users anonymously submit workplace confessions and rate others' suffering.

## Architecture & Tech Stack

The application supports two architectures:
1. **Monolithic Mode (2-Tier)**: FastAPI hosts the API and serves static assets directly, reading/writing from a local SQLite database (`ottoke.db`).
2. **Microservices Mode (3-Tier)**: Decoupled services orchestrated via Docker Compose or Kubernetes, using Nginx for static file delivery and reverse proxying, PostgreSQL for relational storage, and Redis for session caching/rate limiting.

```mermaid
graph TD
    User([User Browser]) -->|HTTP / HTTPS| Ingress[K8s Ingress Controller / Nginx]
    
    Ingress -->|Path: /*| Frontend[Frontend Service: Nginx Container]
    Ingress -->|Path: /api/*| Backend[Backend Service: FastAPI Container]
    
    Backend -->|Read/Write| Postgres[(Database: PostgreSQL Container)]
    Backend -->|Caching & Rate Limits| Redis[(Cache: Redis Container)]
```

### Component Breakdown
*   **Frontend (Presentation Tier)**: Decoupled `nginxinc/nginx-unprivileged` container serving static HTML, CSS, and JS files, and proxying backend queries. Runs under an unprivileged user listening on port `8080`.
*   **Backend (Application Logic Tier)**: FastAPI application running in a hardened non-root container, returning JSON API endpoints.
*   **Database (Data Tier)**: PostgreSQL in containerized/production setups, or a local SQLite (`ottoke.db`) file.
*   **Cache**: Redis cache instance to manage atomic, time-windowed IP rate limits.

## Security Features
- **SQL Injection Prevention:** Strict use of parameterized queries (`?` or `%s`) via sqlite/psycopg2.
- **XSS Prevention:** Frontend text escaping using client-side DOM assignments and backend `html.escape` sterilizations.
- **Rate Limiting:** Lightweight custom rate limiter. Uses atomic Redis caches when available (falling back to database logs), allowing maximum 5 confession submissions, 10 votes, and 10 comments per IP per hour.
- **Session Tracking:** Unique session hashes enforced using `IP + User-Agent + salt`.
- **CORS Protection:** Enforces dynamic `ALLOWED_ORIGINS` setup via backend configuration.

---

## Local Development

You can run this project locally using either **Docker Compose (Recommended)** or **Native Python (SQLite)**.

### Option A: Running with Docker Compose (3-Tier PostgreSQL + Redis)
This matches the production-grade multi-container environment:

1. **Clone the repository**.
2. **Environment Variables**: Create a `.env` file in the root folder (or copy `.env.example`):
   ```env
   POSTGRES_USER=ottoke
   POSTGRES_PASSWORD=ottoke_secure_password
   POSTGRES_DB=ottoke
   DATABASE_URL=postgresql://ottoke:ottoke_secure_password@postgres:5432/ottoke
   REDIS_URL=redis://redis:6379/0
   ALLOWED_ORIGINS=*
   ```
3. **Run the containers**:
   ```bash
   docker compose up --build
   ```
4. **Access the application** at 👉 **[http://localhost:8000](http://localhost:8000)**.
5. **Inspect Redis Cache**:
   ```bash
   docker compose exec redis redis-cli KEYS "*"
   ```
6. **Teardown**:
   ```bash
   docker compose down -v
   ```

### Option B: Running Natively (SQLite Dev Mode)
This runs the app locally without Docker containers:

1. **Prerequisites**: Ensure you have Python 3.11+ installed.
2. **Setup Virtual Environment & Install Dependencies**:
   *   **On Windows (PowerShell)**:
       ```powershell
       .\venv\Scripts\Activate.ps1
       pip install -r requirements.txt
       ```
   *   **On Windows (CMD)**:
       ```cmd
       venv\Scripts\activate.bat
       pip install -r requirements.txt
       ```
   *   **On macOS/Linux**:
       ```bash
       source venv/bin/activate
       pip install -r requirements.txt
       ```
3. **Environment Variables**: Create a `.env.local` in the root:
   ```env
   ALLOWED_ORIGINS=http://localhost:8000
   ```
4. **Seed Database**: Initialize local SQLite file:
   ```bash
   python scripts/seed_db.py
   ```
5. **Run the Server**:
   ```bash
   uvicorn api.index:app --reload
   ```
6. **Access the application** at 👉 **[http://localhost:8000](http://localhost:8000)**.

---

## Deployment
For Kubernetes orchestration configurations, see the manifests stored in the [k8s/](file:///c:/Users/hriti/project/Ottoke/k8s/) folder. For custom standalone Python hostings, run Uvicorn targeting `api.index:app`.

## Easter Eggs 🐣
- **Konami Code:** Have your keyboard ready on the Feed or Leaderboard! Tap `Up Up Down Down Left Right Left Right B A` to enter *K-drama Mode*, overriding the confession titles!
- **Secret 3:33 PM rating message:** Rate any confession at exactly 3:33 PM local time to receive the blessing of the drama gods.

## License
MIT License

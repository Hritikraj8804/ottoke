# Ottoke - Rate My Suffering

A full-stack web application where users anonymously submit workplace confessions and rate others' suffering.

## Architecture & Tech Stack
- **Frontend:** HTML5, TailwindCSS, Vanilla JS
## Database
We are currently running on a local **SQLite** database which stores everything internally in a small `ottoke.db` file. No Postgres service is needed!

## Security Features
- **SQL Injection Prevention:** Strict use of parameterized queries (`?`) via `sqlite3`. No string concatenation for SQL statements.
- **XSS Prevention:** Frontend text escaping using `createElement`/`textContent` analogues, and backend `html.escape` to ensure user content is sterilized before storage in the DB.
- **Rate Limiting:** Lightweight custom backend rate limiter. Checks IP hash and time window to prevent spam. Maximum 5 confession submissions, 10 votes, and 10 comments per IP per hour.
- **Session Tracking:** Unique sessions enforced using an `IP + User-Agent + salt` hashing mechanism. Allows only one vote per confession per user.
- **CORS Protection:** Enforces dynamic `ALLOWED_ORIGINS` setup via backend configuration.

## Local Development
1. Clone the repository.
2. Ensure you have Python 3.11+ installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env.local` file explicitly indicating the allowed URL origin:
   ```env
   ALLOWED_ORIGINS=http://localhost:8000
   ```
5. Initialize the database and seed the daily quotes:
   ```bash
   python scripts/seed_db.py
   ```
6. Run the application locally using Uvicorn:
   ```bash
   uvicorn api.index:app --reload
   ```
   *Note: Open `http://localhost:8000` in your browser to view the frontend.*

## Deployment
This app can be deployed anywhere Python is supported (e.g., Render, Railway, fly.io, Heroku, or a generic VPS). Just ensure Uvicorn is executed to start `api.index:app`. Because it uses a local SQLite state, avoid strictly ephemeral filesystems for long term use.

## Easter Eggs 🐣
- **Konami Code:** Have your keyboard ready on the Feed or Leaderboard! Tap `Up Up Down Down Left Right Left Right B A` to enter *K-drama Mode*, overriding the confession titles!
- **Secret 3:33 PM rating message:** Rate any confession at exactly 3:33 PM local time to receive the blessing of the drama gods.

## License
MIT License

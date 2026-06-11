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

### 1. Prerequisites
Ensure you have **Python 3.11+** installed on your system.

### 2. Setup Virtual Environment & Install Dependencies
A virtual environment `venv` is already included. You can use it or create a new one:

#### On Windows (PowerShell):
```powershell
# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

#### On Windows (Command Prompt / CMD):
```cmd
# Activate the virtual environment
venv\Scripts\activate.bat

# Install required dependencies
pip install -r requirements.txt
```

#### On macOS / Linux:
```bash
# Activate the virtual environment
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a file named `.env.local` in the root of the project with the following content (or modify the existing one):
```env
ALLOWED_ORIGINS=http://localhost:8000
```

### 4. Seed Database
Initialize and seed the SQLite database with daily quotes and tables:
```bash
python scripts/seed_db.py
```

### 5. Run the Application
Start the Uvicorn development server:
```bash
uvicorn api.index:app --reload
```
Once the server is running, open your web browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

## Deployment
This app can be deployed anywhere Python is supported (e.g., Render, Railway, fly.io, Heroku, or a generic VPS). Just ensure Uvicorn is executed to start `api.index:app`. Because it uses a local SQLite state, avoid strictly ephemeral filesystems for long term use.

## Easter Eggs 🐣
- **Konami Code:** Have your keyboard ready on the Feed or Leaderboard! Tap `Up Up Down Down Left Right Left Right B A` to enter *K-drama Mode*, overriding the confession titles!
- **Secret 3:33 PM rating message:** Rate any confession at exactly 3:33 PM local time to receive the blessing of the drama gods.

## License
MIT License

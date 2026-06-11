FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for postgres support)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

# Seed database
RUN python scripts/seed_db.py

# Expose FastAPI port
EXPOSE 8000

# Start app
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
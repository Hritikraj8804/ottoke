FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for PostgreSQL support)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire workspace (context should be the root of the project)
COPY . .

# Create a non-root group and user
RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

# Set proper ownership of the app directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Start app
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]

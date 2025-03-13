FROM python:3.12.4-slim
WORKDIR /app

# Install dependencies first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure the alembic.ini file and migration scripts are copied
COPY alembic.ini .
COPY alembic alembic

# Run as non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000

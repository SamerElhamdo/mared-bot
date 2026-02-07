FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy web requirements and install Python dependencies
COPY web/requirements.txt /app/web/requirements.txt
RUN pip install --no-cache-dir -r /app/web/requirements.txt

# Copy entire project (database, services, config, bot, web)
# This allows web service to import from project root
COPY database /app/database
COPY services /app/services
COPY config /app/config
COPY bot /app/bot
COPY web /app/web

# Expose port
EXPOSE 8000

# Run startup check and then web server
CMD ["sh", "-c", "python web/startup_check.py && uvicorn web.main:app --host 0.0.0.0 --port 8000"]


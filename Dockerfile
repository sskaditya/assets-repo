# Build stage not required for this app; single-stage image
FROM python:3.12-slim

# Prevent Python from writing pyc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# DB and app config — pass at build time
ARG DB_USER_NAME
ARG DB_NAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG SECRET_KEY_ENV
ARG DEBUG
ARG AWS_S3_BUCKET_STATIC_FILES_BUCKET_KEY
ARG AWS_S3_SECRET_KEY_ID_STATIC_FILES
ARG AWS_S3_BUCKET_URL
ARG AWS_S3_BUCKET_NAME
ARG DB_SCHEMA
ENV DB_USER_NAME=$DB_USER_NAME
ENV DB_NAME=$DB_NAME
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV SECRET_KEY_ENV=$SECRET_KEY_ENV
ENV DEBUG=$DEBUG
ENV AWS_S3_BUCKET_STATIC_FILES_BUCKET_KEY=$AWS_S3_BUCKET_STATIC_FILES_BUCKET_KEY
ENV AWS_S3_SECRET_KEY_ID_STATIC_FILES=$AWS_S3_SECRET_KEY_ID_STATIC_FILES
ENV AWS_S3_BUCKET_URL=$AWS_S3_BUCKET_URL
ENV AWS_S3_BUCKET_NAME=$AWS_S3_BUCKET_NAME
ENV DB_SCHEMA=$DB_SCHEMA

WORKDIR /app

# Runtime lib for PostgreSQL (psycopg2-binary uses pre-built wheels; no gcc needed)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# App listens on 8000 (Gunicorn default)
EXPOSE 8000

# Run Gunicorn; bind to 0.0.0.0 so the server is reachable outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "assetz.wsgi:application"]

# Imagen del backend (API Flask). Contexto de construcción: raíz del repositorio.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Guatemala \
    DB_SCRIPTS_DIR=/srv/database

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /srv/backend/
COPY database/ /srv/database/

EXPOSE 5000
CMD ["sh", "-c", "gunicorn --preload --workers 2 --timeout 60 --bind 0.0.0.0:${PORT:-5000} wsgi:app"]

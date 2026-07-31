FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TESSERACT_PATH=/usr/bin/tesseract \
    POPPLER_PATH=/usr/bin \
    PORT=10000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p uploads \
    && adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 10000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers ${WEB_CONCURRENCY:-1} --timeout ${WEB_TIMEOUT:-120} app:app"]

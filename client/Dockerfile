FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN useradd --create-home --uid 10001 appuser && mkdir -p /data && chown appuser:appuser /data
COPY fedcure_client.py .
USER appuser

CMD ["python", "fedcure_client.py"]

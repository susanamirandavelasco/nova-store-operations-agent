# Nova local demo — one worker, fictional orders, no public exposure.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NOVA_DB_PATH=/data/nova_state.sqlite3

WORKDIR /app

COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt \
    && groupadd --system nova \
    && useradd --system --gid nova --home-dir /app nova \
    && mkdir -p /data \
    && chown nova:nova /data

COPY nova/ ./nova/
USER nova

EXPOSE 8000
CMD ["uvicorn", "nova.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-app.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-app.txt


FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY api/   ./api/
COPY ui/    ./ui/
COPY rag/   ./rag/
COPY agent/ ./agent/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

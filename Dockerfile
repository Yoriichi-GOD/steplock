FROM node:24-alpine AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.lock.txt /app/requirements.lock.txt
RUN pip install --no-cache-dir -r requirements.lock.txt && useradd --uid 10001 --create-home steplock
COPY backend/ /app/backend/
COPY recipes/ /app/recipes/
COPY demo_kit/ /app/demo_kit/
COPY fixtures/synthetic/catalog.json /app/fixtures/synthetic/catalog.json
COPY fixtures/synthetic/*_00.avi /app/fixtures/synthetic/
COPY --from=frontend /build/dist /app/frontend/dist
RUN mkdir /app/runtime && chown steplock:steplock /app/runtime
USER steplock
ENV PYTHONUNBUFFERED=1 STEPLOCK_RUNTIME=/app/runtime ENABLE_NEBIUS_AGENT=0
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

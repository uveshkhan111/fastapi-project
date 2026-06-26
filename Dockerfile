# --- Build Stage ---
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim AS runner
WORKDIR /app

# Create a non-root user for security
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY app/ .

ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
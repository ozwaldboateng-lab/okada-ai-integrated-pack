FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY apps/okada-kernel-service /app/apps/okada-kernel-service
RUN pip install --no-cache-dir -e .[dev]

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--app-dir", "apps/okada-kernel-service", "--host", "0.0.0.0", "--port", "8080"]

FROM python:3.12-slim

WORKDIR /app

# install dependencies first (cached if pyproject.toml hasn't changed)
COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

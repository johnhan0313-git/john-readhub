FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
RUN uv pip install --system .

COPY app ./app

ENV DATABASE_URL=postgresql+psycopg://readhub:readhub@postgres:5432/readhub

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

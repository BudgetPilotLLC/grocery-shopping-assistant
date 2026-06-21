FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app ./app
COPY data ./data
COPY docs ./docs
COPY web ./web
COPY README.md ./

EXPOSE 8787

CMD ["python", "-m", "app.server", "--host", "0.0.0.0", "--port", "8787"]


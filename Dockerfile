FROM python:3.13-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install uv==0.9.7 \
    && uv pip install --system -r requirements.txt

COPY .mypy.ini .
COPY src/ ./src/

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY domains ./domains
COPY web ./web
COPY scripts ./scripts

# applications are stored here; mounted as a volume in docker-compose.yml
RUN mkdir -p /app/data
ENV VELAN_DATA_DIR=/app/data

EXPOSE 3000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]

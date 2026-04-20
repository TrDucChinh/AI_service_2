FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8027

CMD ["gunicorn", "recommendation_service.wsgi:application", "--bind", "0.0.0.0:8027", "--workers", "2"]

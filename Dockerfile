FROM python:3.12-slim

WORKDIR /opt

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools>=65.0.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl -fsS http://localhost/health || exit 1

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "main:app"]
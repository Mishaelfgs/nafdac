FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Phase 2 will add: RUN apt-get install -y tesseract-ocr
EXPOSE 8000
# Render/Railway set $PORT. Run ONE process: the queue is in memory (see app/jobs.py).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

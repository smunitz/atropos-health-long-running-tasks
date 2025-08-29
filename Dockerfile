FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/index.html ./templates/index.html
COPY frontend/main.js ./static/main.js

# Flask port
EXPOSE 5000

# Container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()" || exit 1

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
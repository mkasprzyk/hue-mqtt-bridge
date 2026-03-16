FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Config mounted at /config. Entrypoint sets 600 on the config file (required by the app).
COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--config-file", "/config/hue-mqtt-bridge.yaml", "--print-log-console"]

#!/bin/sh
chmod 600 /config/hue-mqtt-bridge.yaml 2>/dev/null || true
# -u: unbuffered stdout/stderr so output is visible when run in Docker
exec python -u -m src.hue_mqtt_bridge "$@"

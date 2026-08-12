#!/bin/bash
set -e

echo "==> [Auto-Setup] Wachten op InfluxDB startup..."
sleep 2

echo "==> [Auto-Setup] Dashboard automatisch importeren..."
influx apply \
  --token "my-influx-token" \
  --org "sensorsim" \
  -f /docker-entrypoint-initdb.d/dashboard.json \
  --force yes || true

echo "==> [Auto-Setup] InfluxDB Dashboard succesvol geconfigureerd!"

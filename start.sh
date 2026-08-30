#!/bin/sh
set -e

# Render/Railway/Fly inject PORT for the public-facing port.

export PORT="${PORT:-8080}"
envsubst '${PORT}' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/sites-enabled/default

echo "Starting VIRA API on :8000..."
cd /app/api

# Seed demo data

python -m app.seed || echo "Seed step skipped or already applied."

# Start backend

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Starting VIRA web on :3000..."
cd /app/web

# Start frontend

npm run start -- -p 3000 &
WEB_PID=$!

echo "Starting nginx on :${PORT}..."
nginx -g "daemon off;" &
NGINX_PID=$!

# POSIX-compatible process monitoring

# Keep the container alive while nginx is running.

wait "$NGINX_PID"
STATUS=$?

echo "nginx exited with status ${STATUS}. Shutting down VIRA..."

kill "$API_PID" "$WEB_PID" 2>/dev/null || true
wait "$API_PID" 2>/dev/null || true
wait "$WEB_PID" 2>/dev/null || true

exit "$STATUS"

#!/bin/sh
set -e

# Render/Railway/Fly inject PORT for the public-facing port; nginx listens
# there and reverse-proxies to the backend (8000) and frontend (3000),
# which stay internal to the container.
export PORT="${PORT:-8080}"
envsubst '${PORT}' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/sites-enabled/default

echo "Starting VIRA API on :8000..."
cd /app/api

# Auto-seed demo data on first boot so the deployed link is usable immediately
# without needing shell access to the container. Safe to run on every boot --
# app/seed.py checks for existing demo data and exits early if already seeded.
python -m app.seed || echo "Seed step skipped or already applied."

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Starting VIRA web on :3000..."
cd /app/web
npm run start -- -p 3000 &
WEB_PID=$!

echo "Starting nginx on :${PORT}..."
nginx -g "daemon off;" &
NGINX_PID=$!

# If any of the three processes dies, bring the whole container down so the
# platform restarts it -- avoids running in a half-broken state silently.
wait -n "$API_PID" "$WEB_PID" "$NGINX_PID"
echo "One of the VIRA processes exited -- shutting down."
kill "$API_PID" "$WEB_PID" "$NGINX_PID" 2>/dev/null
exit 1

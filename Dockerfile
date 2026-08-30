# Combined VIRA image: Next.js frontend + FastAPI backend + nginx, all in one
# container behind a single port. Deploy this as one service (Render/Railway/
# Fly/any Docker host) and you get one URL for the whole app.

FROM node:20-slim AS web-builder
WORKDIR /build
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx nodejs npm gettext-base curl \
    && rm -rf /var/lib/apt/lists/*

# --- Backend ---
WORKDIR /app/api
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/ .

# --- Frontend (built assets + a minimal runtime install for `next start`) ---
WORKDIR /app/web
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install --omit=dev --no-audit --no-fund
COPY --from=web-builder /build/.next ./.next
COPY apps/web/next.config.js ./

# --- nginx + startup ---
COPY nginx.conf.template /etc/nginx/templates/nginx.conf.template
RUN rm -f /etc/nginx/sites-enabled/default
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD curl -f http://127.0.0.1:${PORT}/health || exit 1

CMD ["/app/start.sh"]

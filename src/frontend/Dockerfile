# Documented in: docs/RUNLOCAL.md, docs/deployment/runbook.md
# Multi-stage build for the MAIVE React/Vite frontend.
# Builder produces /app/dist; runtime uses nginx:alpine to serve it.

# ---------- Builder ----------
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# ---------- Runtime ----------
FROM nginx:alpine AS runtime

# Default backend URL for SPA proxy; override at container start.
ENV BACKEND_URL="http://backend:8000"

# Use envsubst at container start to render nginx.conf with $BACKEND_URL.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

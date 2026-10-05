# syntax=docker/dockerfile:1

# ---- Build stage: compile the static assets ----
FROM node:24-alpine AS builder

WORKDIR /app

# Dependencies first: this layer is cached as long as the lockfile does not change.
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# ---- Runtime stage: static files served by an unprivileged nginx ----
FROM nginxinc/nginx-unprivileged:1.30-alpine AS runtime

# Rendered at startup by the image entrypoint (envsubst), into /etc/nginx/conf.d/.
COPY nginx/security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

# Address of the API, used by the /api reverse proxy.
ENV VOTELY_API_UPSTREAM=http://backend:8000

USER 101

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/healthz"]

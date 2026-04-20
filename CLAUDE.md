# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Production-grade e-commerce platform built with Django microservices (backend), React + Vite (frontend), and an API Gateway. 25+ containerized services orchestrated via Docker Compose.

---

## Common Commands

### Start the full platform
```bash
docker compose up --build        # Build images and start all services
docker compose up -d             # Detached mode
docker compose down              # Stop all services
docker compose logs -f <service> # Stream logs for one service
```

### Database migrations (run inside a container)
```bash
docker compose exec auth-service python manage.py migrate
docker compose exec laptop-service python manage.py migrate
```

### Seed product data
```bash
# Seed a single service
docker compose exec laptop-service python manage.py seed_products

# Seed all 15 product services at once
bash infra/seed_all.sh
```

### Seed default roles (auth service)
```bash
docker compose exec auth-service python manage.py create_default_roles
```

### Frontend (local development without Docker)
```bash
cd frontend
npm install
npm run dev      # Vite dev server on :3000, proxies /api → localhost:8000
npm run build    # Production build → dist/
```

### Access a service shell
```bash
docker compose exec <service-name> bash
# e.g.: docker compose exec gateway bash
```

### Run a Django management command on any service
```bash
docker compose exec <service> python manage.py <command>
```

---

## Architecture

### Request Flow
```
Browser → Nginx (:80) → API Gateway (:8000) → downstream services
                    ↗ (static)  Frontend (:80)
```

In local dev, the Vite server (:3000) proxies `/api/*` directly to the gateway (:8000).

### API Gateway (`gateway/`)
All client traffic enters through the gateway. Three middleware layers run in order:
1. **LoggingMiddleware** — logs every request with user ID, role, and duration
2. **RateLimitMiddleware** — 100 req / 60 s per IP (in-memory store)
3. **JWTValidationMiddleware** — enforces RBAC:
   - Public paths (login, register, health) bypass auth
   - GET on `/api/products/`, `/api/search/`, `/api/recommendations/`, `/api/inventory/` are public
   - Everything else requires a valid Bearer token
   - Product write ops require `staff` or `admin` role
   - `/api/auth/users/` and `/api/auth/roles/` writes require `admin` role

The gateway decodes the JWT locally (no round-trip to auth-service) using `JWT_SECRET_KEY`. On success it injects `X-User-ID`, `X-User-Email`, `X-User-Role`, `X-User-Username` headers before proxying downstream.

### Service Map

| Category | Services | Ports | DB |
|----------|----------|-------|----|
| Business | auth, user, cart, order, payment | 8001–8005 | MySQL |
| Products | laptop, mobile, tablet, audio, accessory, smartwatch, camera, monitor, keyboard, mouse, printer, networking, storage, component, gaminggear | 8010–8024 | PostgreSQL (one DB each) |
| Utility | search, notification, recommendation, inventory | 8025–8028 | Redis / SQLite |
| Workers | celery-order-worker, celery-payment-worker, celery-notification-worker | — | — |
| Infra | mysql, postgres, redis, nginx | 3306, 5432, 6379, 80 | — |
| Monitoring | celery-flower | 5555 | — |

### Inter-Service Communication
- All services communicate over the Docker network `ecommerce_net` using service hostnames (e.g. `http://auth-service:8001`).
- Service URLs are configured via `.env` and read with `python-decouple`.
- Async work (order confirmation emails, payment processing, inventory updates) flows through Celery with Redis as broker (`redis://redis:6379/1`) and result backend (`redis://redis:6379/2`).

### Product Services (identical structure)
All 15 product services share the same Django app layout (`apps/products/`). The canonical reference implementation is `products/laptop-service/`. Each has:
- `ProductViewSet` with Redis caching (5-min TTL on `retrieve`, invalidated on update/delete)
- `IsAdminOrReadOnly` permission (reads public, writes require `X-User-Role: admin` or `staff`)
- `seed_products` management command for test data
- Separate PostgreSQL database named `product_<category>`

### Auth / JWT
- Auth service issues JWTs via `djangorestframework-simplejwt`. Tokens carry `user_id`, `email`, `role`, `username` claims.
- Roles: `admin`, `staff`, `customer` (stored on `CustomUser.role_name`).
- The gateway validates tokens using `PyJWT` directly — no request to auth-service per call.
- Refresh token rotation is supported; revoked tokens are tracked in the `auth_refresh_tokens` table.

### Frontend (`frontend/src/`)
- **Routing**: React Router v6 in `App.jsx` — protected routes use `<ProtectedRoute>` (auth) and `<AdminRoute>` (admin/staff).
- **Server state**: React Query (`@tanstack/react-query`) for all API data.
- **Client state**: Redux Toolkit — `authSlice` (persisted to localStorage) and `cartSlice`.
- **API client**: `src/api/axios.js` — attaches Bearer token automatically; auto-refreshes on 401 and retries the original request.
- **Product API**: `src/api/products.js` — `productsApi.list(service, params)` and `productsApi.get(service, id)` route to the correct product service via the gateway.

### Caching Strategy (Redis)
| Data | TTL | Key pattern |
|------|-----|-------------|
| Product detail | 300 s | `product_{pk}` |
| All categories | 3600 s | `all_categories` |
| Recommendations | 300 s | `reco:{service}:{product_id}:{limit}` |
| Inventory aggregate | 60 s | `inventory:aggregate` |
| Low-stock list | 60 s | `inventory:low_stock:{threshold}:{filter}` |

---

## Environment Configuration

All services read from the root `.env` file via `python-decouple`. Key variables:

```
JWT_SECRET_KEY          # Must match across gateway and all services
JWT_ALGORITHM=HS256
MYSQL_HOST / MYSQL_PASSWORD / etc.
POSTGRES_HOST / POSTGRES_PASSWORD / etc.
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
EMAIL_BACKEND           # Set to smtp for production
LOW_STOCK_THRESHOLD=10
```

---

## Adding a New Product Service

1. Copy an existing product service (e.g. `products/laptop-service/`) to `products/<name>-service/`.
2. Update `<service_name>/settings.py`: change `POSTGRES_DB` environment variable and service name.
3. Add the service to `docker-compose.yml` following the existing product service pattern.
4. Add the URL to `gateway/gateway_service/settings.py` in `PRODUCT_SERVICE_URLS`.
5. Add the URL constant to `frontend/src/api/products.js` in `PRODUCT_SERVICES` and `SERVICE_LABELS`.
6. Add the hostname to `search/apps/search/views.py` in the service list.
7. Add it to `infra/seed_all.sh`.

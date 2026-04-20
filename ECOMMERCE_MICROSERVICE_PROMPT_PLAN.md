
# E-Commerce Microservice Platform — Full Prompt Plan

## Overview

This document provides a structured prompt execution plan for generating a production-grade
microservice e-commerce system using Claude Code 

Stack:
- Backend: Django (microservices)
- Frontend: React + TailwindCSS
- Gateway: Django API Gateway
- Databases:
  - MySQL (auth + business services)
  - PostgreSQL (product services)
- Containerization: Docker
- Auth: JWT + RBAC
- Dataset: Real product datasets (Kaggle / DummyJSON / FakeStoreAPI)

Follow prompts sprint-by-sprint to avoid generation errors.

---

# Sprint 1 Prompt — Infrastructure Setup

Prompt:

Create the base microservice repository structure:

services/
products/
gateway/
frontend/
infra/

Setup docker-compose.yml with:

mysql container
postgres container

Create base Django template service structure reusable across services.

Add environment variable support (.env).

Include health check endpoint:

/health/

Expected Result:

docker compose up runs MySQL and PostgreSQL successfully.

---

# Sprint 2 Prompt — Auth Service

Prompt:

Create auth-service using Django and MySQL.

Features:

register
login
logout
refresh token
JWT issuing
RBAC role assignment

Tables:

users
roles
permissions
user_roles
role_permissions
refresh_tokens

Endpoints:

POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh

Expected Result:

JWT authentication working.

---

# Sprint 3 Prompt — User + Cart Services

Prompt:

Create user-service:

profile management
addresses
wishlist

Tables:

profiles
addresses
wishlists

Create cart-service:

add item
remove item
update quantity
view cart

Tables:

cart
cart_items

Expected Result:

Customer cart lifecycle functional.

---

# Sprint 4 Prompt — Order + Payment Services

Prompt:

Create order-service:

create order
cancel order
order history
status tracking

Tables:

orders
order_items
order_status_logs

Create payment-service:

mock payment gateway
COD support
transaction tracking

Tables:

payments
transactions

Expected Result:

Checkout flow functional.

---

# Sprint 5 Prompt — Core Product Services

Prompt:

Create PostgreSQL-based product services:

laptop-service
mobile-service
tablet-service
audio-service
accessory-service

Each service must include:

products
brands
categories
images
inventory
reviews
ratings

Expected Result:

Core catalog operational.

---

# Sprint 6 Prompt — Extended Product Services

Prompt:

Create additional services:

smartwatch-service
camera-service
monitor-service
keyboard-service
mouse-service
printer-service
networking-service
storage-service
component-service
gaminggear-service

Expected Result:

15 product services operational.

---

# Sprint 7 Prompt — API Gateway

Prompt:

Create gateway service:

JWT validation middleware
request routing
rate limiting
logging middleware
error handling

Routes:

/api/auth/*
/api/users/*
/api/cart/*
/api/orders/*
/api/products/*

Expected Result:

Unified API entry point operational.

---

# Sprint 8 Prompt — Search Aggregator

Prompt:

Create search aggregator service:

query multiple product services
merge results
return unified response

Optional:

Elasticsearch integration

Expected Result:

Cross-service search operational.

---

# Sprint 9 Prompt — React Frontend

Prompt:

Create React frontend using:

TailwindCSS
Redux Toolkit
React Query
Framer Motion

Customer pages:

Home
Product listing
Product detail
Cart
Checkout
Profile
Order history

Admin pages:

Dashboard
User management
Product management
Analytics

Staff pages:

Inventory panel
Order processing panel

Expected Result:

Frontend connected to gateway.

---

# Sprint 10 Prompt — Dataset Seeding

Prompt:

Import datasets from:

Kaggle
FakeStoreAPI
DummyJSON

Pipeline:

CSV
→ ETL script
→ Django management command
→ PostgreSQL

Expected Result:

Real catalog populated.

---

# Sprint 11 Prompt — RBAC Enforcement

Prompt:

Implement role-based access control:

ADMIN
STAFF
CUSTOMER

Apply enforcement:

gateway middleware
service decorators
endpoint-level validation

Expected Result:

Permissions enforced correctly.

---

# Sprint 12 Prompt — Optimization Layer

Prompt:

Add:

Redis caching
Celery workers
Email notifications
Recommendation service
Inventory service
Elasticsearch search

Optimize:

query performance
pagination
indexing
caching

Expected Result:

Production-ready architecture complete.

---

# Final Expected Outcome

System includes:

15 product microservices
JWT authentication
RBAC authorization
API Gateway routing
React production UI
Docker deployment
Real datasets
Search aggregation
Scalable architecture

#!/bin/bash
# Seed all product services with sample data

SERVICES=(
  "laptop-service:8010"
  "mobile-service:8011"
  "tablet-service:8012"
  "audio-service:8013"
  "accessory-service:8014"
  "smartwatch-service:8015"
  "camera-service:8016"
  "monitor-service:8017"
  "keyboard-service:8018"
  "mouse-service:8019"
  "printer-service:8020"
  "networking-service:8021"
  "storage-service:8022"
  "component-service:8023"
  "gaminggear-service:8024"
)

echo "=== Seeding all product services ==="
for entry in "${SERVICES[@]}"; do
  service="${entry%%:*}"
  echo "Seeding $service..."
  docker compose exec "$service" python manage.py seed_products
done
echo "=== Seeding complete ==="

#!/bin/sh
# Load sample products (HASH product:001 ...)
docker compose exec -T redis redis-cli < seed/seed.redis && echo "Seed done"

#!/bin/sh
# Create the product index (drops the old one first)
docker compose exec -T redis redis-cli FT.DROPINDEX idx:products >/dev/null 2>&1
docker compose exec -T redis redis-cli FT.CREATE idx:products ON HASH PREFIX 1 product: \
  SCHEMA \
    name TEXT WEIGHT 5.0 \
    brand TEXT \
    category TAG \
    price NUMERIC SORTABLE \
    rating NUMERIC SORTABLE \
    stock NUMERIC

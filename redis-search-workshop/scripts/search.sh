#!/bin/sh
# Usage: ./scripts/search.sh [name] [min_price] [max_price] [asc|desc]
# Examples:
#   ./scripts/search.sh wireless 50 200
#   ./scripts/search.sh mouse "" 70 desc     (no min)
#   ./scripts/search.sh "" 300               (price only)
NAME=$(printf '%s' "$1" | tr -c '[:alnum:] ' ' ')   # strip query-syntax characters
MIN=${2:--inf}; [ -z "$MIN" ] && MIN="-inf"
MAX=${3:-+inf}; [ -z "$MAX" ] && MAX="+inf"
ORDER=${4:-asc}

TEXT="*"
if [ -n "$(echo $NAME)" ]; then
  TEXT=""
  for w in $NAME; do TEXT="$TEXT @name:$w*"; done
fi
QUERY="$TEXT @price:[$MIN $MAX]"
echo "Query: $QUERY"
docker compose exec -T redis redis-cli FT.SEARCH idx:products "$QUERY" \
  RETURN 3 name price brand SORTBY price "$ORDER" LIMIT 0 20

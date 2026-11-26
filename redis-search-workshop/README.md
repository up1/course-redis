# Workshop: Product Search with Redis Search & Query (Redis 8.12 + Docker Compose)

**Goal:** search products by **name** and filter by **price range** using the Redis Query Engine (`FT.*` commands).
**Time:** ~60 min · **Level:** beginner

Redis 8 ships the Query Engine built in, so plain `redis:8.x` is enough (no Redis Stack, no module loading).
Docs: https://redis.io/docs/latest/develop/ai/search-and-query/

## What you will learn
1. Run Redis 8.12 with Docker Compose
2. Store products as HASHes
3. Create a search index (`FT.CREATE`) with TEXT / TAG / NUMERIC fields
4. Search by name, filter by price, sort, paginate
5. Fuzzy and prefix matching, aggregations
6. Wrap it in shell scripts

## 0. Prerequisites
Docker + Docker Compose v2.

## 1. Start the stack

```bash
docker compose up -d
./scripts/seed.sh                   # loads 20 products as product:001 ... product:020
```

> Only Docker, a shell and `redis-cli` (inside the container) are used.
>
> Image defaults to `redis:8.12-rc2` (8.12 was still in release-candidate when this was written).
> Once `redis:8.12` is published: `REDIS_IMAGE=redis:8.12 docker compose up -d`.

Open a shell:

```bash
docker compose exec redis redis-cli
```

Check the engine is present and look at the data:

```
127.0.0.1:6379> MODULE LIST        # Query Engine appears as "search"
127.0.0.1:6379> HGETALL product:001
127.0.0.1:6379> DBSIZE             # 20
```

## 2. Data model

Each product is a HASH:

| field | example | index type |
|---|---|---|
| name | Wireless Earbuds Pro | TEXT (weight 5) |
| brand | Apple | TEXT |
| category | audio | TAG |
| price | 249.0 | NUMERIC, SORTABLE |
| rating | 4.6 | NUMERIC, SORTABLE |
| stock | 80 | NUMERIC |

## 3. Create the index

```
FT.CREATE idx:products ON HASH PREFIX 1 product:
  SCHEMA
    name     TEXT WEIGHT 5.0
    brand    TEXT
    category TAG
    price    NUMERIC SORTABLE
    rating   NUMERIC SORTABLE
    stock    NUMERIC
```

(Or run `./scripts/create-index.sh`.) The 20 existing keys are indexed in the background; new `product:*` keys are indexed automatically.

```
FT.INFO idx:products               # check num_docs = 20, indexing = 0
```

## 4. Search by name

```
FT.SEARCH idx:products "@name:wireless"
FT.SEARCH idx:products "wireless"                  # searches all TEXT fields (name + brand)
FT.SEARCH idx:products "@name:(wireless keyboard)"  # both words (AND)
FT.SEARCH idx:products "@name:(keyboard|mouse)"     # either word (OR)
FT.SEARCH idx:products "@name:wire*"                # prefix
FT.SEARCH idx:products "@name:%wirelss%"            # fuzzy, 1 typo allowed
```

Return only the fields you need:

```
FT.SEARCH idx:products "@name:wireless" RETURN 3 name price brand
```

## 5. Filter by price range

Numeric ranges use square brackets, **inclusive**. `(` makes a bound exclusive. `-inf` / `+inf` are open ends.

```
FT.SEARCH idx:products "@price:[50 200]"          # 50 ≤ price ≤ 200
FT.SEARCH idx:products "@price:[(50 (200]"        # 50 < price < 200
FT.SEARCH idx:products "@price:[-inf 50]"         # up to 50
FT.SEARCH idx:products "@price:[200 +inf]"        # 200 and up
```

## 6. Combine name + price (the main use case)

```
FT.SEARCH idx:products "@name:wireless @price:[50 200]"
  RETURN 2 name price
  SORTBY price ASC
```

Expected: Wireless Keyboard Slim (59.99), Wireless Gaming Mouse (79.99). Wireless Earbuds Pro (249) and the Sony headphones (299.99) are out of range.

Equivalent with the `FILTER` argument (keeps the query text clean, handy when building queries in code):

```
FT.SEARCH idx:products "@name:wireless" FILTER price 50 200 RETURN 2 name price SORTBY price
```

Add a category and rating filter:

```
FT.SEARCH idx:products "@name:wireless @category:{computer} @price:[(50 +inf] @rating:[4.5 +inf]"
```

## 7. Sort and paginate

```
FT.SEARCH idx:products "@price:[0 100]" SORTBY price DESC LIMIT 0 5   # page 1
FT.SEARCH idx:products "@price:[0 100]" SORTBY price DESC LIMIT 5 5   # page 2
```

## 8. Aggregations (price buckets, averages)

```
FT.AGGREGATE idx:products "*"
  GROUPBY 1 @category
  REDUCE COUNT 0 AS items
  REDUCE AVG 1 @price AS avg_price
  REDUCE MIN 1 @price AS cheapest
  SORTBY 2 @avg_price DESC
```

Average price of products matching a search:

```
FT.AGGREGATE idx:products "@name:wireless" GROUPBY 0 REDUCE AVG 1 @price AS avg_price
```

## 9. Keep the index live

Index updates are automatic:

```
HSET product:021 name "Wireless Trackball Mouse" brand "Kensington" price 55 category computer rating 4.3 stock 12
FT.SEARCH idx:products "@name:trackball @price:[50 60]" RETURN 2 name price

HSET product:021 price 99            # price change is reflected immediately
DEL product:021                      # removed from the index
```

## 10. Shell scripts

`scripts/search.sh [name] [min] [max] [asc|desc]` builds the query for you and strips query-syntax characters from user input.

```bash
./scripts/search.sh wireless 50 200
./scripts/search.sh mouse "" 70 desc      # max price only
./scripts/search.sh "" 300                # price filter only
```

## Exercises

1. Find all **audio** products under $100, cheapest first.
2. Find products whose name contains *keyboard* **or** *monitor*, priced 50–450.
3. Search for `"wirless"` (typo) and still get wireless products.
4. Add a `description` TEXT field to the index (`FT.ALTER`) and search it.
5. Show the 3 best-rated products per category (hint: `GROUPBY` + `REDUCE TOLIST` or `SORTBY` + `LIMIT`).
6. `FT.EXPLAIN` your combined query and read how Redis parses it.

<details><summary>Solutions</summary>

```
1. FT.SEARCH idx:products "@category:{audio} @price:[-inf (100]" SORTBY price ASC
2. FT.SEARCH idx:products "@name:(keyboard|monitor) @price:[50 450]"
3. FT.SEARCH idx:products "@name:%wirless%"
4. FT.ALTER idx:products SCHEMA ADD description TEXT
5. FT.AGGREGATE idx:products "*" SORTBY 2 @rating DESC GROUPBY 1 @category REDUCE FIRST_VALUE 2 @name BY @rating AS top_product
6. FT.EXPLAIN idx:products "@name:wireless @price:[50 200]"
```
</details>

## Troubleshooting

| Problem | Fix |
|---|---|
| `unknown command 'FT.CREATE'` | Not running Redis 8+. Check `docker compose exec redis redis-server --version`. |
| `Index already exists` | `FT.DROPINDEX idx:products` (add `DD` to also delete the documents). |
| Search returns 0 | `FT.INFO idx:products` and make sure `indexing` is 0 and `num_docs` is 20. Keys must start with `product:`. |
| Hyphenated words | Characters like `-`, `@`, `{`, `[` are query syntax; escape with `\` or strip them. |
| `redis:8.12` not found | Use the default `redis:8.12-rc2`, or any `redis:8` tag. |

## Clean up

```bash
docker compose down -v
```

## Next steps
- Index as **JSON** instead of HASH (`ON JSON`, `$.price AS price NUMERIC`)
- Add **vector search** for semantic product search ("something to listen to music while running")
- Stemming/stopwords/synonyms (`FT.SYNUPDATE`), highlighting (`HIGHLIGHT`), suggestions (`FT.SUGADD`)

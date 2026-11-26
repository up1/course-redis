# Workshop: Semantic product search with Redis vector search

**Goal:** find products by *meaning*, e.g. `"something to listen to music while running"` -> earbuds, headphones, fitness band.
Keyword search cannot do this: none of those words appear in the product names.

**Time:** ~45 min · **Data:** `../seed/seed.redis` (20 products) · **Embeddings:** [`BAAI/bge-small-en-v1.5`](https://huggingface.co/BAAI/bge-small-en-v1.5) (384 dims)

## 0. Prerequisites
Docker Compose v2, Python 3.10+.

```bash
cd demo-vector-search
docker compose up -d            # Redis 8 on localhost:6380 (Query Engine built in)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Override with `REDIS_PORT=...`, `REDIS_IMAGE=...` (compose) or `REDIS_HOST/REDIS_PORT` (python).

## Files
| file | purpose |
|---|---|
| `docker-compose.yml` | Redis 8 |
| `common.py` | seed parser, model loader, helpers |
| `step1_embed.py` | embed + store + create index |
| `step2_vector_search.py` | pure semantic KNN search |
| `step3_hybrid_search.py` | filters + vector, text + vector (RRF) |

## Step 1 - Embedding with BGE
```bash
python step1_embed.py
```
- Parses the `HSET` lines in `seed.redis` (no `redis-cli` loading needed).
- Text to embed = `"<name> by <brand>, category: <category>"`.
- BGE model turns it into 384 floats, normalized. Stored as `FLOAT32` bytes in field `embedding` of each `product:*` HASH.
- Index: `TEXT/TAG/NUMERIC` + `VECTOR HNSW DIM 384 DISTANCE_METRIC COSINE`.

Equivalent raw command:
```
FT.CREATE idx:product:vec ON HASH PREFIX 1 product: SCHEMA
  name TEXT WEIGHT 5 brand TEXT category TAG price NUMERIC SORTABLE rating NUMERIC SORTABLE
  embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE
```

## Step 2 - Vector search
```bash
python step2_vector_search.py
python step2_vector_search.py "gift for a gamer"
```
Query is embedded with the **same model**, with BGE's query instruction prefix, then:
```
FT.SEARCH idx:product:vec "*=>[KNN 5 @embedding $vec AS vector_score]" PARAMS 2 vec <blob> SORTBY vector_score DIALECT 2
```
`vector_score` is cosine distance: smaller = more similar.

**Try:** "work comfortably at a desk all day", "record my skiing trip", "keep my phone alive while travelling".

## Step 3 - Hybrid search
```bash
python step3_hybrid_search.py
python step3_hybrid_search.py "cheap speaker for the beach"
```
- **A. Filtered KNN** - structured filters + similarity in one query:
  `(@category:{audio} @price:[0 200])=>[KNN 5 @embedding $vec AS vector_score]`
- **B. Text + vector fusion** - BM25 ranking and vector ranking merged with Reciprocal Rank Fusion
  `score = Σ 1/(60 + rank)`. Items found by both lists rise to the top.
  Redis 8.4+ also offers this server-side as `FT.HYBRID`.

## Exercises
1. Change `HNSW` to `FLAT`; compare results.
2. Add a `description` to products and re-embed; does ranking improve?
3. Use `BAAI/bge-base-en-v1.5` (`EMBED_MODEL=... `, set `DIM = 768`).
4. Add `@stock:[1 +inf]` to the filter in step 3A.

## Clean up
```bash
docker compose down -v
```

"""Step 1 - embed the products with a BGE model and store them in Redis.

  seed.redis -> text -> BGE embedding (384 floats) -> HASH field `embedding` -> FT.CREATE index
"""
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType

from common import DIM, INDEX, MODEL_NAME, PREFIX, get_redis, load_model, load_products, product_text, to_blob

r = get_redis()
r.ping()

# 1) read data from seed.redis
products = load_products()
print(f"Parsed {len(products)} products from seed.redis")

# 2) embed (documents: NO instruction prefix)
print(f"Loading model {MODEL_NAME} (first run downloads it from Hugging Face)...")
model = load_model()
keys = list(products)
texts = [product_text(products[k]) for k in keys]
vectors = model.encode(texts, normalize_embeddings=True, batch_size=32)
print(f"Embedded -> shape {vectors.shape}")

# 3) store: the original fields + the vector as binary
pipe = r.pipeline()
for key, vec in zip(keys, vectors):
    pipe.hset(key, mapping={**products[key], "embedding": to_blob(vec)})
pipe.execute()

# 4) index: TEXT/TAG/NUMERIC for classic filters + VECTOR for semantic search
try:
    r.ft(INDEX).dropindex(delete_documents=False)
except Exception:
    pass

r.ft(INDEX).create_index(
    [
        TextField("name", weight=5.0),
        TextField("brand"),
        TagField("category"),
        NumericField("price", sortable=True),
        NumericField("rating", sortable=True),
        VectorField(
            "embedding",
            "HNSW",  # or "FLAT" for exact search on small data
            {"TYPE": "FLOAT32", "DIM": DIM, "DISTANCE_METRIC": "COSINE"},
        ),
    ],
    definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH),
)
print(f"Index {INDEX} created")
info = r.ft(INDEX).info()
print("num_docs =", info["num_docs"], "| indexing failures =", info.get("hash_indexing_failures"))

"""Shared helpers for the vector-search workshop."""
import os
import re
import shlex
from pathlib import Path

import numpy as np
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))

INDEX = "idx:product:vec"
PREFIX = "product:"

# bge-small: 384 dims, ~130MB, fast on CPU. Swap for BAAI/bge-base-en-v1.5 (768) if you like.
MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
DIM = 384
# bge uses an instruction prefix for *queries* only (not for documents)
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

SEED_FILE = Path(os.getenv("SEED_FILE") or Path(__file__).resolve().parent.parent / "seed" / "seed.redis")


def get_redis() -> redis.Redis:
    # decode_responses stays False: vectors are raw bytes
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def load_products() -> dict[str, dict[str, str]]:
    """Parse `HSET key f v f v ...` lines of seed.redis -> {key: {field: value}}."""
    products = {}
    for line in SEED_FILE.read_text().splitlines():
        line = line.strip()
        if not line.upper().startswith("HSET "):
            continue
        _, key, *rest = shlex.split(line)
        products[key] = dict(zip(rest[0::2], rest[1::2]))
    return products


def product_text(p: dict[str, str]) -> str:
    """The text we embed. The seed has no description, so we compose one."""
    return f"{p['name']} by {p['brand']}, category: {p['category']}"


def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def to_blob(vec) -> bytes:
    """Redis wants FLOAT32 little-endian bytes."""
    return np.asarray(vec, dtype=np.float32).tobytes()


def embed_query(model, text: str) -> bytes:
    # normalize_embeddings=True -> unit vectors, so COSINE == inner product
    return to_blob(model.encode(QUERY_PREFIX + text, normalize_embeddings=True))


def print_rows(rows, cols=("name", "brand", "category", "price")):
    for i, r in enumerate(rows, 1):
        extra = "  ".join(f"{c}={r[c]}" for c in cols if c in r)
        score = f"  [{r['score']}]" if "score" in r else ""
        print(f"{i:>2}. {r['id']:<12} {extra}{score}")

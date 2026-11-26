"""Step 2 - semantic (vector) search.

  query text -> BGE embedding -> KNN over the HNSW index -> nearest products

Usage: python step2_vector_search.py "something to listen to music while running"
"""
import sys

from redis.commands.search.query import Query

from common import INDEX, embed_query, get_redis, load_model, print_rows

queries = sys.argv[1:] or [
    "something to listen to music while running",
    "work comfortably at a desk all day",
    "record my skiing trip",
    "keep my phone alive while travelling",
]

r = get_redis()
model = load_model()

for text in queries:
    blob = embed_query(model, text)
    # KNN 5: "the 5 closest vectors". vector_score = cosine distance (0 = identical).
    q = (
        Query("*=>[KNN 5 @embedding $vec AS vector_score]")
        .sort_by("vector_score")
        .return_fields("name", "brand", "category", "price", "vector_score")
        .dialect(2)
    )
    res = r.ft(INDEX).search(q, query_params={"vec": blob})

    print(f'\n=== "{text}" ===')
    rows = [
        {
            "id": d.id,
            "name": d.name,
            "brand": d.brand,
            "category": d.category,
            "price": d.price,
            "score": f"dist={float(d.vector_score):.3f}",
        }
        for d in res.docs
    ]
    print_rows(rows)

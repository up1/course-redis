"""Step 3 - hybrid search: vector similarity + classic search.

  A) Filtered KNN   : TAG / NUMERIC filter and KNN in ONE query (pre-filtering)
  B) Text + vector  : BM25 full-text ranking and KNN ranking fused with RRF
                      (Reciprocal Rank Fusion) - done client-side so it works on any Redis 8

Usage: python step3_hybrid_search.py "something to listen to music while running"
"""
import sys

from redis.commands.search.query import Query

from common import INDEX, embed_query, get_redis, load_model, print_rows

text = " ".join(sys.argv[1:]) or "something to listen to music while running"
r = get_redis()
model = load_model()
blob = embed_query(model, text)
FIELDS = ("name", "brand", "category", "price", "vector_score")


def to_rows(res, score_fn):
    return [
        {"id": d.id, "name": d.name, "brand": d.brand, "category": d.category,
         "price": d.price, "score": score_fn(d)}
        for d in res.docs
    ]


# ---------------------------------------------------------------- A) filtered KNN
print(f'\n=== A) "{text}"  +  category=audio  AND  price <= 200 ===')
flt = "(@category:{audio} @price:[0 200])"
q = (
    Query(f"{flt}=>[KNN 5 @embedding $vec AS vector_score]")
    .sort_by("vector_score")
    .return_fields(*FIELDS)
    .dialect(2)
)
res = r.ft(INDEX).search(q, query_params={"vec": blob})
print_rows(to_rows(res, lambda d: f"dist={float(d.vector_score):.3f}"))

# ---------------------------------------------------------------- B) text + vector (RRF)
KEYWORDS = sys.argv[1:] and " ".join(sys.argv[1:]) or "wireless | bluetooth | headphones | earbuds"
print(f'\n=== B) RRF fusion: BM25 text query "{KEYWORDS}" + vector query "{text}" ===')

TOP = 10
# ranking 1: full-text (BM25)
text_q = Query(KEYWORDS).return_fields(*FIELDS).paging(0, TOP).dialect(2)
text_docs = r.ft(INDEX).search(text_q).docs
# ranking 2: vector
vec_q = (
    Query(f"*=>[KNN {TOP} @embedding $vec AS vector_score]")
    .sort_by("vector_score").return_fields(*FIELDS).paging(0, TOP).dialect(2)
)
vec_docs = r.ft(INDEX).search(vec_q, query_params={"vec": blob}).docs

K = 60  # standard RRF constant
fused, meta = {}, {}
for ranking in (text_docs, vec_docs):
    for rank, d in enumerate(ranking, 1):
        fused[d.id] = fused.get(d.id, 0.0) + 1.0 / (K + rank)
        meta[d.id] = d

print(f"text hits: {len(text_docs)}   vector hits: {len(vec_docs)}")
rows = [
    {"id": i, "name": meta[i].name, "brand": meta[i].brand, "category": meta[i].category,
     "price": meta[i].price, "score": f"rrf={s:.4f}"}
    for i, s in sorted(fused.items(), key=lambda kv: -kv[1])[:5]
]
print_rows(rows)

print("""
Note: Redis 8.4+ can do this fusion server-side with FT.HYBRID
(SEARCH ... VSIM ... COMBINE RRF). The client-side version above shows what it does.""")

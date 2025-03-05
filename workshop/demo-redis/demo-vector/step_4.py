import numpy as np
from redis.commands.search.query import Query
import os
import redis
from redis.commands.search.query import Query
import pandas as pd
from sentence_transformers import SentenceTransformer
pd.set_option('display.max_colwidth', None)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# If SSL is enabled on the endpoint, use rediss:// as the URL prefix
REDIS_URL = f"redis://:{REDIS_HOST}:{REDIS_PORT}"
INDEX_NAME = f"thaifood:index"


redis = redis.Redis(
  host=REDIS_HOST,
  port=REDIS_PORT
)

# Using paraphrase-multilingual-MiniLM-L12-v2 model which supports 50+ languages
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
def texts_to_embeddings(texts):
  return [np.array(embedding, dtype=np.float32).tobytes() for embedding in model.encode(texts, show_progress_bar=True)]


# Search for a query
user_query="ไข่"
query_vector=texts_to_embeddings([user_query])[0]
q = Query("*=>[KNN 20 @text_embedding $vector AS vector_score]")\
    .return_fields("vector_score", "name")\
    .dialect(2)\
    .sort_by("vector_score")\
    .paging(0, 10)\
    .timeout(5000)  # 5 second timeout
params_dict = {"vector": query_vector}
results = redis.ft(INDEX_NAME).search(q, query_params=params_dict)

for i, result in enumerate(results.docs):
    score = 1 - float(result.vector_score)
    print(f"{i}. {result.name} (Score: {round(score ,3) })")
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
pd.set_option('display.max_colwidth', None)

# Load the dataset from huggingface datasets :: https://huggingface.co/datasets/pythainlp/thai_food_v1.0
df = pd.read_parquet("hf://datasets/pythainlp/thai_food_v1.0/data/train-00000-of-00001-e8b362f32bb3715c.parquet")
print(df.shape)
# show only name column
print(df.head()["name"])

# Embed the text using SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def texts_to_embeddings(texts):
  return [np.array(embedding, dtype=np.float32).tobytes() for embedding in model.encode(texts, show_progress_bar=True)]


df["text_embedding"] = texts_to_embeddings(df["name"].tolist())
print("Embedding done")

# Save the dataset to redis server
import os
import redis
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.field import VectorField, TextField, NumericField


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# If SSL is enabled on the endpoint, use rediss:// as the URL prefix
REDIS_URL = f"redis://:{REDIS_HOST}:{REDIS_PORT}"
INDEX_NAME = f"thaifood:index"


redis = redis.Redis(
  host=REDIS_HOST,
  port=REDIS_PORT
)

def create_redis_index(redis, idxname="thaifood:index"):
  try:
    redis.ft(idxname).dropindex()
  except:
    print("no index found")

  # Create an index
  indexDefinition = IndexDefinition(
      prefix=["thaifood:"],
      index_type=IndexType.HASH,
  )

  redis.ft(idxname).create_index(
      (
          TextField("name", no_stem=False, sortable=False),
          VectorField("text_embedding", "HNSW", {  "TYPE": "FLOAT32",
                                                    "DIM": 384,
                                                    "DISTANCE_METRIC": "COSINE",
                                                  })
      ),
      definition=indexDefinition
  )
   

redis.flushdb()
create_redis_index(redis, INDEX_NAME)

# Load data to redis
def load_dataframe(redis, df, key_prefix="thaifood", id_column="id", pipe_size=100):
    records = df.to_dict(orient="records")
    pipe = redis.pipeline(transaction=False)
    i = 1
    for record in records:
        i += 1  # Using shorthand += for increment
        key = f"{key_prefix}:{i}"
        record[id_column] = key
        pipe.hset(key, mapping=record)
        if i % pipe_size == 0:
            pipe.execute()
    pipe.execute()

load_dataframe(redis, df, key_prefix="thaifood", id_column="id")
print("Data loaded to redis")


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
# Using paraphrase-multilingual-MiniLM-L12-v2 model which supports 50+ languages
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
def texts_to_embeddings(texts):
  return [np.array(embedding, dtype=np.float32).tobytes() for embedding in model.encode(texts, show_progress_bar=True)]


df["text_embedding"] = texts_to_embeddings(df["name"].tolist())
print(df.shape)
print(df.head()["text_embedding"])
     

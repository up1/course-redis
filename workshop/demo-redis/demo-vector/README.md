# Workshop :: Vector database with Redis

## Step 0 :: Create virtual environment
```
$python -m venv ./demo/venv
$source ./demo/venv/bin/activate
```

## Step 1 :: Install dependencies
```
$pip install -r requirements.txt
```

## Step 2 :: Test connection to Redis server
```
$python step_1.py
```

## Step 3 :: Load dataset and embedding
```
$python step_2.py
```

## Step 4 :: Save vector data into Redis
```
$python step_3.py
```

## Step 5 :: Search data in Redis
```
$python step_4.py
```

### Reference websites
* [Redis vector database](https://redis.io/docs/latest/develop/get-started/vector-database/)
* [Using Redis as a vector database with OpenAI](https://cookbook.openai.com/examples/vector_databases/redis/getting-started-with-redis-and-openai)
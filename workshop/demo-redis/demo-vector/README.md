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

## Run with docker compose

Build image
```
$docker compose build
```

Create redis server
```
$docker compose up -d redis

$docker compose ps
NAME                  IMAGE               COMMAND            SERVICE   CREATED         STATUS         PORTS
demo-vector-redis-1   redis/redis-stack   "/entrypoint.sh"   redis     6 seconds ago   Up 6 seconds   6379/tcp, 8001/tcp
```

Embedding and save to redis
```
$docker compose up embedding
```

Search data from redis
```
$docker compose up search
```

### Reference websites
* [Redis vector database](https://redis.io/docs/latest/develop/get-started/vector-database/)
* [Using Redis as a vector database with OpenAI](https://cookbook.openai.com/examples/vector_databases/redis/getting-started-with-redis-and-openai)
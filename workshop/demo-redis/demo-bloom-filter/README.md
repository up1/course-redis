# Demo with [Bloom filter](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)

```
A Bloom filter is a space-efficient probabilistic data structure that quickly checks if an element is probably in a set
```

## 1. Start Redis server
```
$docker compose up -d redis
$docker compose ps
```

Access to redis
```
$docker compose exec -it redis bash
$redis-cli
```

## 2. Compare data size (Add 100,000 emails)
* [SET](https://redis.io/docs/latest/commands/set/)
* [BF.ADD](https://redis.io/docs/latest/commands/bf.add/)

### SET operation
```
$docker compose down
$docker compose up -d redis

$docker compose up demo-set --build
```

### BF.ADD operation
```
$docker compose down
$docker compose up -d redis

$docker compose up demo-bloom-filter --build
```

### Monitor in redis-cli
* DBSIZE => number of keys
* FLUSHALL => delete all keys
* KEYS *
* INFO MEMORY 


## 3. Start demo app with Bloom filter
* Check email is existed in system ?
```
$docker compose build api
$docker compose up -d api
$docker compose ps
```

URL for testing
* http://localhost:8080/users/your-email
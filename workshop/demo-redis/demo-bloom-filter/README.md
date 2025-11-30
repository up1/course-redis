# Demo with [Bloom filter](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)

```
A Bloom filter is a space-efficient probabilistic data structure that quickly checks if an element is probably in a set
```

## 1. Start Redis server
```
$docker compose up -d redis
$docker compose ps
```

## 2. Compare data size (Add 100,000 emails)
* [SET](https://redis.io/docs/latest/commands/set/)
* [BF.ADD](https://redis.io/docs/latest/commands/bf.add/)

### SET operation
```
$go run main_data_size_1.go
```

### BF.ADD operation
```
$$go run main_data_size_2.go
```

### Monitor in redis-cli
* DBSIZE => number of keys
* FLUSHALL => delete all keys
* KEYS *
* INFO MEMORY 


## 3. Start demo app
* Check email is existed in system ?
```
$go mod tidy
$go run main.go
```

URL for testing
* http://localhost:8080/users/emayour-email
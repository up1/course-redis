# Connection pool with redis

## Start redis
```
$docker container run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack
```

## Run server
```
$go mod tidy
$go run main.go
```


## Benchmark
```
$go test -bench=. -benchmem
```
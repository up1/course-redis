# Redis Standalone mode
* For development and testing only

## Start node

```
# Start containers
$docker compose -f docker-compose.single.yml up -d redis1

$docker compose -f docker-compose.single.yml ps
NAME                IMAGE     COMMAND                  SERVICE   CREATED         STATUS         PORTS
workshop-redis1-1   redis:7   "docker-entrypoint.s…"   redis1    4 seconds ago   Up 4 seconds   6379/tcp
```

## Working with redis

```
// Write
$docker compose -f docker-compose.single.yml exec -T redis1 redis-cli -p 6379 INCR counter

// Read
$docker compose -f docker-compose.single.yml exec -T redis1 redis-cli -p 6379 GET counter
```

Access to container
```
$docker compose -f docker-compose.single.yml exec -it redis1 bash
$redis-cli
```

## Working with Monitoring
* Prometheus
* [Redis exporter](https://github.com/oliver006/redis_exporter)

```
$docker compose -f docker-compose.single.yml up -d redis-exporter
$docker compose -f docker-compose.single.yml up -d prometheus

$docker compose -f docker-compose.single.yml ps
NAME                        IMAGE                      COMMAND                  SERVICE          CREATED          STATUS          PORTS
workshop-prometheus-1       prom/prometheus            "/bin/prometheus --c…"   prometheus       24 seconds ago   Up 17 seconds   0.0.0.0:9090->9090/tcp
workshop-redis-exporter-1   oliver006/redis_exporter   "/redis_exporter"        redis-exporter   32 seconds ago   Up 28 seconds   0.0.0.0:9121->9121/tcp
workshop-redis1-1           redis:7                    "docker-entrypoint.s…"   redis1           3 minutes ago    Up 3 minutes    6379/tcp
```

Access to prometheus in web browser
* http://localhost:9090/


## Delete all resources
```
$docker compose -f docker-compose.single.yml down
```

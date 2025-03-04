# [Redis Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
Designed for high availability without Cluster

## Node roles
* `Master` node for write data
* `Slave` node for read data

## Responsesibiliries
* Monitoring for (Master and Slave nodes)
* Notification to external systems (Prometheus, Grafana, NewRelic .. etc.)
* Automatic failover
* Configuration provider


## Sentinel
Required minimum nodes = 3 nodes
* Master = 1
* Slave = 2

Default configurations
* SENTINEL_QUORUM: 2
* SENTINEL_DOWN_AFTER: 5000
* SENTINEL_FAILOVER: 5000


```
# Build image
$docker compose -f docker-compose.sentinel.yml build 

# Start containers
$docker compose -f docker-compose.sentinel.yml up -d

$docker compose -f docker-compose.sentinel.yml ps
NAME                  IMAGE               COMMAND                  SERVICE    CREATED         STATUS         PORTS
workshop-master-1     redis:7             "docker-entrypoint.s…"   master     4 seconds ago   Up 3 seconds   6379/tcp
workshop-sentinel-1   workshop-sentinel   "entrypoint.sh"          sentinel   4 seconds ago   Up 3 seconds   6379/tcp
workshop-slave-1      redis:7             "docker-entrypoint.s…"   slave      4 seconds ago   Up 3 seconds   6379/tcp
```

## Scale number of sentinel nodes
```
$docker compose -f docker-compose.sentinel.yml up -d --scale sentinel=3
```

## Scale number of slave nodes
```
$docker compose -f docker-compose.sentinel.yml up -d --scale slave=3
```

## Get information of sentinel
```
$docker compose -f docker-compose.sentinel.yml exec sentinel redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
```

## Working with redis

1. Write data from to master node
```
$docker compose -f docker-compose.sentinel.yml exec -T master redis-cli -p 6379 INCR counter
```

2. Read to slave node
```
$docker compose -f docker-compose.sentinel.yml exec -T slave redis-cli -p 6379 GET counter
```

## Delete all resources
```
$docker compose -f docker-compose.sentinel.yml down
```

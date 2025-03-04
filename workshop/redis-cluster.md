# Redis cluster = Replication + Shading data

## Cluster
Required minimum nodes = 6 nodes (production)
* Master = 3
* Slave = 3

## 1. Start Redis Node with Cluster mode
```
$cd cluster
$docker compose up -d redis1
$docker compose up -d redis2
$docker compose up -d redis3

$docker-compose ps

NAME               IMAGE     COMMAND                  SERVICE   CREATED         STATUS         PORTS
cluster-redis1-1   redis:7   "docker-entrypoint.s…"   redis1    8 seconds ago   Up 8 seconds   
cluster-redis2-1   redis:7   "docker-entrypoint.s…"   redis2    6 seconds ago   Up 6 seconds   
cluster-redis3-1   redis:7   "docker-entrypoint.s…"   redis3    4 seconds ago   Up 4 seconds   
```

## 2. Create cluster with replication = 0
* Master 3 nodes
* Slave 0 nodes
```
$docker compose up  -d redis-cluster
$docker compose logs  redis-cluster

redis-cluster_1  | >>> Performing hash slots allocation on 3 nodes...
redis-cluster_1  | Master[0] -> Slots 0 - 5460
redis-cluster_1  | Master[1] -> Slots 5461 - 10922
redis-cluster_1  | Master[2] -> Slots 10923 - 16383
redis-cluster_1  | M: 3958296b5f349d6a5fec74aeaed5bf94c81029d7 127.0.0.1:7000
redis-cluster_1  |    slots:[0-5460] (5461 slots) master
redis-cluster_1  | M: 2c7fe6ee16055c514727124d6c72738314cfaecb 127.0.0.1:7001
redis-cluster_1  |    slots:[5461-10922] (5462 slots) master
redis-cluster_1  | M: 3677a9ae34d109912b7d1e8b868656794fa82489 127.0.0.1:7002
redis-cluster_1  |    slots:[10923-16383] (5461 slots) master
redis-cluster_1  | Can I set the above configuration? (type 'yes' to accept): >>> Nodes configuration updated
redis-cluster_1  | >>> Assign a different config epoch to each node
redis-cluster_1  | >>> Sending CLUSTER MEET messages to join the cluster
redis-cluster_1  | Waiting for the cluster to join
redis-cluster_1  | ...
redis-cluster_1  | >>> Performing Cluster Check (using node 127.0.0.1:7000)
redis-cluster_1  | M: 3958296b5f349d6a5fec74aeaed5bf94c81029d7 127.0.0.1:7000
redis-cluster_1  |    slots:[0-5460] (5461 slots) master
redis-cluster_1  | M: 2c7fe6ee16055c514727124d6c72738314cfaecb 127.0.0.1:7001
redis-cluster_1  |    slots:[5461-10922] (5462 slots) master
redis-cluster_1  | M: 3677a9ae34d109912b7d1e8b868656794fa82489 127.0.0.1:7002
redis-cluster_1  |    slots:[10923-16383] (5461 slots) master
redis-cluster_1  | [OK] All nodes agree about slots configuration.
redis-cluster_1  | >>> Check for open slots...
redis-cluster_1  | >>> Check slots coverage...
redis-cluster_1  | [OK] All 16384 slots covered.
redis-cluster_1  | cluster_redis-cluster_1 exited with code 0


$docker-compose ps

NAME               IMAGE     COMMAND                  SERVICE   CREATED          STATUS          PORTS
cluster-redis1-1   redis:7   "docker-entrypoint.s…"   redis1    20 seconds ago   Up 20 seconds   
cluster-redis2-1   redis:7   "docker-entrypoint.s…"   redis2    18 seconds ago   Up 18 seconds   
cluster-redis3-1   redis:7   "docker-entrypoint.s…"   redis3    17 seconds ago   Up 16 seconds   
```

Check your cluster on node 1
```
$docker container exec -it cluster-redis1-1 bash
$redis-cli -c -p 7000
$set name hello

-> Redirected to slot [5798] located at 127.0.0.1:7001
OK

>get name
"hello"

```

## Delete all resources
```
$docker compose down
```

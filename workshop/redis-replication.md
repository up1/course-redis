# Redis Replication
Designed for scale read operations

## Node roles
* `Master` node for write data
* `Slave` node for read data

```
# Start containers
$docker compose -f docker-compose.replication.yml up -d 

$docker compose -f docker-compose.replication.yml ps
       Name                      Command               State    Ports
-----------------------------------------------------------------------
workshop_master_1     docker-entrypoint.sh redis ...   Up      6379/tcp
workshop_slave_1      docker-entrypoint.sh redis ...   Up      6379/tcp
```

## Scale number of slave nodes
```
$docker compose -f docker-compose.replication.yml up -d --scale slave=3

$docker compose -f docker-compose.replication.yml ps
NAME                IMAGE     COMMAND                  SERVICE   CREATED          STATUS          PORTS
workshop-master-1   redis:7   "docker-entrypoint.s…"   master    32 seconds ago   Up 29 seconds   0.0.0.0:6379->6379/tcp
workshop-slave-1    redis:7   "docker-entrypoint.s…"   slave     32 seconds ago   Up 29 seconds   6379/tcp
workshop-slave-2    redis:7   "docker-entrypoint.s…"   slave     9 seconds ago    Up 2 seconds    6379/tcp
workshop-slave-3    redis:7   "docker-entrypoint.s…"   slave     9 seconds ago    Up 3 seconds    6379/tcp
```

## Working with redis

1. Write data from to master node
```
$docker compose -f docker-compose.replication.yml exec -T master redis-cli -p 6379 INCR counter
```

2. Read to slave node
```
$docker compose -f docker-compose.replication.yml exec -T slave redis-cli -p 6379 GET counter
```

## Delete all resources
```
$docker compose -f docker-compose.replication.yml down
```

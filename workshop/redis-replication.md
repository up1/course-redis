# Redis Replication
Designed for scale read operations

## Node roles
* `Master` node for write data
* `Slave` node for read data

## Start master nodes
```
$docker compose -f docker-compose.replication.yml up -d master
$docker compose -f docker-compose.replication.yml ps
```

## Start slave nodes
```
$docker compose -f docker-compose.replication.yml up -d slave1
$docker compose -f docker-compose.replication.yml up -d slave2
$docker compose -f docker-compose.replication.yml up -d slave3
$docker compose -f docker-compose.replication.yml ps
```

## Check status of all nodes
```
$docker compose -f docker-compose.replication.yml exec -T master redis-cli info Replication
```

## Write data from to master node
```
$docker compose -f docker-compose.replication.yml exec -T master redis-cli -p 6379 INCR counter
```

### Read to slave node (slave 1, 2, 3)
```
$docker compose -f docker-compose.replication.yml exec -T slave1 redis-cli -p 6379 GET counter

$docker compose -f docker-compose.replication.yml exec -T slave2 redis-cli -p 6379 GET counter

$docker compose -f docker-compose.replication.yml exec -T slave3 redis-cli -p 6379 GET counter
```

## Delete all resources
```
$docker compose -f docker-compose.replication.yml down
```

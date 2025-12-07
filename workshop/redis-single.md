# Redis Standalone mode
* For development and testing only

## Start Redis server

```
# Start containers
$docker compose -f docker-compose.single.yml up -d redis1

$docker compose -f docker-compose.single.yml ps
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
* [Redis exporter](https://github.com/oliver006/redis_exporter)
* [Prometheus](https://prometheus.io/)
* [Grafana](https://grafana.com/)

```
$docker compose -f docker-compose.single.yml up -d redis-exporter
$docker compose -f docker-compose.single.yml up -d prometheus
$docker compose -f docker-compose.single.yml up -d grafana

$docker compose -f docker-compose.single.yml ps
```

Access to prometheus exporter for Redis in web browser
* http://localhost:9121/

Access to prometheus in web browser
* http://localhost:9090/
  * Goto menu => Status => Target health

Access to grafana in web browser
* http://localhost:3000/
  * user=admin
  * password=admin
* Add new datasource
  * http://localhost:3000/connections/datasources
    * Prometheus
    * Prometheus server URL = http://prometheus:9090
* Import [Redis dashboard](https://grafana.com/grafana/dashboards/763-redis-dashboard-for-prometheus-redis-exporter-1-x/)
  * http://localhost:3000/dashboard/import
    * ID=763

## Delete all resources
```
$docker compose -f docker-compose.single.yml down
```

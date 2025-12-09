# Demo Redis,s configuration

## Start Redis with docker + `myredis.conf`
```
$docker compose up -d redis
$docker compose ps
```

## Optimize for a read-heavy workload
* Disable Active Defragmentation (if not needed)
  * Defrag can consume CPU. If memory fragmentation isn't critical, keep it off or tune it conservatively
* Replica Configuration
  * Ensure replicas are read-only.
* IO Threading
  * Redis 6+ (and 8) supports multi-threaded I/O
  * For heavy reads, enabling I/O threads can significantly boost throughput by offloading network writing/reading from the main thread
* TCP Backlog
  * Increase the backlog for high connection rates.
* Save/Persistence
  * If durability is less critical than raw read speed, consider relaxing save parameters or using AOF with everysec

## Basic Benchmark
Run a quick benchmark with 100,000 requests using default settings:
```bash
redis-benchmark -q -n 100000
```

## Benchmark Specific Commands
Test only `SET` and `GET` commands:
```bash
redis-benchmark -t set,get -q -n 100000
```

## Simulate Heavy Load (Pipeline)
Use pipelining to simulate higher throughput (e.g., 16 commands per request):
```bash
redis-benchmark -t set,get -P 16 -q -n 100000
```

## Benchmark with Multi-threaded I/O
If you enabled `io-threads` in your config

```bash
redis-benchmark -t set,get -c 50 -q -n 100000
```


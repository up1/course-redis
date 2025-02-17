## Redis workshop

### Outline
* Data types in Redis
  * String
  * List
  * Set
  * SortedSet
  * Search
* Data modeling in Redis
  * Embedded
  * Partial Embed
  * Aggregate
* Use cases
  * Data caching
  * Session/key management
  * Real-time layer
  * Messaging queue
  * Pub/Sub
  * Geospatial Indexing – Location-Based Services
  * Rate Limiting – Preventing API Abuse
* Redis topology
  * [Single instance](/workshop/README.md)
  * [Replication :: Master-Slaves](/workshop/redis-replication.md)
  * [Sentinel](/workshop/redis-sentinel.md)
  * [Cluster](/workshop/redis-cluster.md)
* Configuration in Redis
  * Memory management
  * Redis persistence
    * RDB (Redis Database)
    * AOF (Append Only File)
    * No persistence
    * RDB + AOF   
* Optimizing Redis
  * Benchmark
  * CPU profiling
  * Diagnosing latency issues
  * Latency monitoring
  * Memory optimization
    * Data Eviction Strategies
      * Least Recently Used (LRU)
      * Least Frequently Used (LFU)
      * Random 
* [Redis monitoring](/workshop/redis-monitoring.md)
  * Prometheus
    * Redis exporter
  * Grafana

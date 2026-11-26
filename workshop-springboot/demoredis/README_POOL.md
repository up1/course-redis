# Connection Pool: PostgreSQL (HikariCP) and Redis (Lettuce)

## Configuration

Set in `src/main/resources/application.properties`. Each pool setting can be overridden with an environment variable.

| Target | Setting | Default | Env override |
|---|---|---|---|
| PostgreSQL (HikariCP) | `maximum-pool-size` | 20 | `DB_POOL_MAX` |
| PostgreSQL (HikariCP) | `minimum-idle` | 20 | `DB_POOL_MIN_IDLE` |
| PostgreSQL (HikariCP) | `connection-timeout` | 2000 ms | |
| PostgreSQL (HikariCP) | `idle-timeout` / `max-lifetime` / `keepalive-time` | 10 min / 30 min / 5 min | |
| Redis (Lettuce) | `lettuce.pool.enabled` | true | |
| Redis (Lettuce) | `max-active` / `max-idle` | 20 | `REDIS_POOL_MAX` |
| Redis (Lettuce) | `min-idle` | 5 | `REDIS_POOL_MIN_IDLE` |
| Redis (Lettuce) | `max-wait` | 500 ms | |

Redis pooling needs the `commons-pool2` dependency, which is in `pom.xml`.

## Steps to run and load test

Prerequisites: Docker, JDK, and [k6](https://k6.io) (`brew install k6`).

1. Start PostgreSQL and Redis:

   ```bash
   docker compose up -d postgres redis
   ```

2. Start the API. A seed of 10,000 users is enough, because the load test only uses ids 1 to 1000:

   ```bash
   APP_SEED_USERS=10000 ./mvnw spring-boot:run
   ```

3. In another terminal, warm the Redis cache so that all hot ids are cached:

   ```bash
   k6 run -e TOTAL=1000 perf/warmup.js
   ```

4. Load test PostgreSQL only (exercises the Hikari pool):

   ```bash
   k6 run -e PATH_PREFIX=/api/user/db -e VUS=100 -e DURATION=20s perf/load.js
   ```

5. Load test Redis with PostgreSQL fallback (exercises the Lettuce pool):

   ```bash
   k6 run -e PATH_PREFIX=/api/user -e VUS=100 -e DURATION=20s perf/load.js
   ```

6. To compare against other pool settings, stop the app and restart it with overrides, then repeat steps 4 and 5:

   ```bash
   # Redis: no pool (one shared connection), Hikari pool of 10
   APP_SEED_USERS=0 \
   SPRING_DATA_REDIS_LETTUCE_POOL_ENABLED=false \
   SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE=10 \
   SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE=10 \
   ./mvnw spring-boot:run
   ```

7. Clean up:

   ```bash
   docker compose down
   ```

## Results

Environment: one local machine. k6, the API, PostgreSQL 17 and Redis 8 all ran on it. There were 100 virtual users for 20 seconds per run, one run per case. There were no failed requests in any run.

| Endpoint | Pool setting | Requests/sec | Avg | p95 |
|---|---|---|---|---|
| `/api/user/db` (PostgreSQL only) | Hikari 20 | 11,080 | 8.98 ms | 19.9 ms |
| `/api/user/db` (PostgreSQL only) | Hikari 10 | 8,959 | 11.11 ms | 21.5 ms |
| `/api/user` (Redis, then PostgreSQL) | Lettuce pool 20 | 31,955 | 3.05 ms | 5.02 ms |
| `/api/user` (Redis, then PostgreSQL) | Lettuce no pool (shared connection) | 33,936 | 2.88 ms | 4.6 ms |

## Conclusions

- **Hikari:** A pool of 20 connections gave about 24% more requests per second than a pool of 10. Keep the larger pool.
- **Redis cache:** Reading through Redis was about 3 times faster than going straight to PostgreSQL.
- **Lettuce pool:** It did not help here. The shared connection was about 6% faster, because the workload is simple GET and SET calls and a pooled call pays to borrow and return a connection. Consider `spring.data.redis.lettuce.pool.enabled=false`. Use the pool only for blocking commands or transactions.
- **Caveats:**
  - Each case ran once.
  - The pooled runs used a freshly seeded database, and the other runs reused it with seeding turned off.
  - Everything shared one machine.
  - Treat the numbers as relative, not absolute.
- **Sizing:** Keep `DB_POOL_MAX` times the number of app instances below PostgreSQL's `max_connections`.

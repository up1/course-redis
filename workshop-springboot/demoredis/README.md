# Workshop :: Spring Boot + Redis + PostgreSQL

REST API `GET user profile by id` (see [req.md](req.md)), feature-based structure:

```
com.example.demoredis
├── common/   ErrorResponse, exceptions, GlobalExceptionHandler (400/404/500)
└── user/     UserController, UserService, UserRepository, User (+Address/Geo/Company), UserDataSeeder
```

## Endpoints

| Endpoint | Data source |
|---|---|
| `GET /api/user/db/{id}` | PostgreSQL only |
| `GET /api/user/{id}` | Redis first (key `user:{id}`, TTL 10m) → on miss read PostgreSQL and populate Redis |

If Redis is down/slow, endpoint 2 logs a warning and falls back to PostgreSQL (no 500).

## Configuration

[application.properties](src/main/resources/application.properties)

| Property | Meaning |
|---|---|
| `spring.data.redis.host/port/database` | Redis location (`REDIS_HOST`, `REDIS_PORT` env override) |
| `spring.data.redis.timeout=500ms` | client command timeout (Spring/Lettuce) |
| `spring.data.redis.connect-timeout=1s` | client connect timeout |
| `app.cache.user-ttl=10m` | TTL of cached users |
| `spring.datasource.url/username/password` | PostgreSQL (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` env override; default `demo`/`demo` on `localhost:5432/demodb`) |
| `app.seed.users=1000000` | users generated in PostgreSQL on first start (0 = off) |

[redis.conf](redis.conf) (server side): `timeout 300` (close idle clients after 300 s), `tcp-keepalive 60`,
`maxmemory 1gb` + `allkeys-lru`, persistence off.

## 1. Steps to run

### Docker (API + Redis + PostgreSQL)
```bash
docker compose up -d --build
docker compose logs -f api        # wait for "Seeded 1000000 users"
curl localhost:8080/api/user/1
```
- If host ports are taken: `REDIS_HOST_PORT=16379 POSTGRES_HOST_PORT=15432 docker compose up -d --build`.
- Stop: `docker compose down` (add `-v` to also drop the PostgreSQL data volume and re-seed next time).

### Local (no Docker for the API)
```bash
docker compose up -d redis postgres   # or your own Redis :6379 / PostgreSQL :5432 (db/user/password: demodb/demo/demo)
./mvnw spring-boot:run
```

## 2. Initial data (1,000,000 users in PostgreSQL)

- Nothing to do: on startup `UserDataSeeder` checks the `users` table and, if empty, inserts ids 1..1,000,000
with one `INSERT ... SELECT FROM generate_series(1, N)` (about 2-3 s).
- Data lives in the `pgdata` volume, so seeding happens only once.
- Users: `id=N`, `name="User N"`, `username="userN"`, ...
- Valid ids are 1–1,000,000; anything else → 404.

Quick checks:
```bash
curl -i localhost:8080/api/user/db/500000   # PostgreSQL only
curl -i localhost:8080/api/user/500000      # miss -> PostgreSQL -> Redis
curl -i localhost:8080/api/user/500000      # hit from Redis
curl -i localhost:8080/api/user/abc         # 400
curl -i localhost:8080/api/user/2000000     # 404
docker compose exec redis redis-cli ttl user:500000
docker compose exec postgres psql -U demo demodb -c 'select count(*) from users'
```

## 3. Performance testing (response time)

Script: [perf/load.js](perf/load.js) ([k6](https://k6.io), 50 VUs, 20 s). `HOT_IDS` = how many distinct ids are requested
(random in 1..HOT_IDS).
```bash
k6 run -e PATH_PREFIX=/api/user/db -e HOT_IDS=1000    perf/load.js   # PostgreSQL, small working set
k6 run -e PATH_PREFIX=/api/user    -e HOT_IDS=1000    perf/load.js   # Redis + PostgreSQL, ~100% hits
k6 run -e PATH_PREFIX=/api/user/db -e HOT_IDS=1000000 perf/load.js   # PostgreSQL, whole table
k6 run -e PATH_PREFIX=/api/user    -e HOT_IDS=1000000 perf/load.js   # Redis + PostgreSQL, cold cache (mostly misses)

# Redis + PostgreSQL, whole table warm: load all 1,000,000 users into Redis first (~1 min, ~500 MB),
# then run the test within the 10 min TTL
docker compose exec redis redis-cli flushall                         # start from a cold cache
k6 run perf/warmup.js
k6 run -e PATH_PREFIX=/api/user    -e HOT_IDS=1000000 perf/load.js
```
- All 1M users need ~500 MB in Redis, which is why `redis.conf` allows `maxmemory 1gb` (with less, LRU eviction would break the 100% hit ratio).
- Single request: `curl -s -o /dev/null -w '%{time_total}\n' localhost:8080/api/user/1`

Result on a laptop (everything in Docker, k6 on the same machine, so indicative only):

| Scenario | avg | p95 | req/s |
|---|---|---|---|
| PostgreSQL only, 1,000 ids | 2.60 ms | 5.17 ms | ~18,900 |
| Redis + PostgreSQL, 1,000 ids (warm, ~100% hits) | 1.94 ms | 2.94 ms | ~25,300 |
| PostgreSQL only, 1,000,000 ids | 2.57 ms | 4.91 ms | ~19,100 |
| Redis + PostgreSQL, 1,000,000 ids (cold cache, mostly misses) | 3.40 ms | 5.18 ms | ~14,500 |
| Redis + PostgreSQL, 1,000,000 ids (warm cache, 100% hits) | 2.20 ms | 3.71 ms | ~22,300 |

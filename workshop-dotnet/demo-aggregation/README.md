# Workshop with Order Report

## 1. Start Redis server
```
$docker compose up -d redis
$docker compose ps
```

## 2. Create Console project
```
$dotnet new console
```

## 3. Install dependencies
```
$dotnet add package StackExchange.Redis
$dotnet add package CsvHelper
```

## 4. Run
```
$dotnet run
```

## 5. Check data in Redis
```
$docker compose exec -it redis bash
$redis-cli

// List of all keys
keys *
1) "report:monthly:2025-12"
2) "report:weekly:2025-W50"
3) "report:daily:2025-12-10"
4) "report:daily:2025-12-05"
5) "report:topspenders"
6) "report:daily:2025-12-06"
7) "report:weekly:2025-W49"

// Delete all keys
FLUSHALL
```
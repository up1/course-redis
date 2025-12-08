# Workshop with Order Report
* Daily/Weekly/Monthly
* Top 10 spenders

## 0. Order data from CSV file
* orders.csv

```
order_id,user_id,amount,timestamp
1001,45,50.99,2025-12-05 10:30:00
1002,12,120.00,2025-12-05 15:45:00
1003,90,25.50,2025-12-06 08:00:00
1004,12,88.00,2025-12-10 12:00:00
```

### Design key in Redis
| Time Period |Redis Key (HASH) |Field (HASH)|Stored Value
|---|---|---|---|
| Daily   | report:daily:<YYYY-MM-DD> | orders / revenue | Count / Sum of Amount
| Weekly  | report:weekly:<YYYY-WNN>  | orders / revenue | Count / Sum of Amount
| Monthly | report:monthly:<YYYY-MM>  | orders / revenue | Count / Sum of Amount

* Top 10 spenders with SortedSet
  * Key=report:topspenders
  * Memeber=user:<user_id>
  * Score=order.Amount

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

## 4. Run app with .NET 8

Run with dotnet command
```
$dotnet run
```

Run with docker
```
$docker compose up demo-report --build
```

## 5. Check data in Redis
```
$docker compose exec -it redis bash
$redis-cli

// Number of all keys
DBSIZE

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

## 6. Remove all resources
```
$docker compose down
```
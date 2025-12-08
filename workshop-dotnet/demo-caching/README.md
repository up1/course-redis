# Workshop :: .NET and Redis
* .NET 8
* Redis


## Create project and install dependencies
* [StackExchange.Redis](https://stackexchange.github.io/StackExchange.Redis/)
```
$dotnet new webapi -n weatherapp
$cd weatherapp
$dotnet add package StackExchange.Redis
```

## Start Redis server
```
$docker compose up -d redis
$docker compose ps
```

Check keys in redis
```
$docker compose exec -it redis bash
$redis-cli
$keys *
```


## Start app with .NET command
```
$dotnet restore
$dotnet run
```

List of URLs
* http://localhost:5251/swagger/index.html
* http://localhost:5251/WeatherForecast?latitude=38.8894&longitude=-77.0352

## Start app with Docker
```
$docker compose build api
$docker compose up -d api
$docker compose ps
```

* http://localhost:5000/swagger/index.html
* http://localhost:5000/WeatherForecast?latitude=38.8894&longitude=-77.0352


## Load test with Docker wrk
```
$docker compose up wrk --build
```

## Remove all resources
```
$docker compose down
```
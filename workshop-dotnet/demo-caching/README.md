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
$docker container run -d -p 6379:6379 redis
$docker container ps
```

## Start app
```
$dotnet restore
$dotnet run
```

List of URLs
* http://localhost:5251/swagger/index.html
* http://localhost:5251/WeatherForecast?latitude=38.8894&longitude=-77.0352
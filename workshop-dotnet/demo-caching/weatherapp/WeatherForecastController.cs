using System.Diagnostics;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.AspNetCore.Mvc;
using StackExchange.Redis;

[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    private readonly HttpClient _client;
    private readonly IDatabase _redis;

    public WeatherForecastController(HttpClient client, IConnectionMultiplexer muxer)
    {
        _client = client;
        _client.DefaultRequestHeaders.UserAgent.Add(new ProductInfoHeaderValue("weatherCachingApp", "1.0"));
        _redis = muxer.GetDatabase();
    }


    [HttpGet(Name = "GetWeatherForecast")]
    public async Task<ForecastResult> Get([FromQuery] double latitude, [FromQuery] double longitude)
    {
        string? json;
        var watch = Stopwatch.StartNew();
        var keyName = $"forecast:{latitude},{longitude}";
        // 1. Try to get from Redis cache
        json = await _redis.StringGetAsync(keyName);
        if (string.IsNullOrEmpty(json))
        {
            Console.WriteLine("Cache miss from Redis");
            // 2. If not found, get from weather API
            json = await GetForecast(latitude, longitude);

            // 3. Store the result in Redis cache with expiration
            var setTask = _redis.StringSetAsync(keyName, json);
            var expireTask = _redis.KeyExpireAsync(keyName, TimeSpan.FromSeconds(3600));
            await Task.WhenAll(setTask, expireTask);
        } else {
            Console.WriteLine("Cache hit from Redis");
        }

        // 4. Deserialize and return the result
        var forecast =
            JsonSerializer.Deserialize<IEnumerable<WeatherForecast>>(json);
        watch.Stop();
        var result = new ForecastResult(forecast ?? Enumerable.Empty<WeatherForecast>(), watch.ElapsedMilliseconds);

        return result;
    }

    private async Task<string> GetForecast(double latitude, double longitude)
    {
        // Write log
        Console.WriteLine($"Fetching forecast for latitude: {latitude}, longitude: {longitude}");
        var pointsRequestQuery = $"https://api.weather.gov/points/{latitude},{longitude}"; //get the URI
        var result = await _client.GetFromJsonAsync<JsonObject>(pointsRequestQuery);
        var gridX = result?["properties"]?["gridX"]?.ToString();
        var gridY = result?["properties"]?["gridY"]?.ToString();
        var gridId = result?["properties"]?["gridId"]?.ToString();
        var forecastRequestQuery = $"https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast";
        var forecastResult = await _client.GetFromJsonAsync<JsonObject>(forecastRequestQuery);
        var periodsJson = forecastResult?["properties"]?["periods"]?.ToJsonString();
        return periodsJson ?? "[]";
    }

}
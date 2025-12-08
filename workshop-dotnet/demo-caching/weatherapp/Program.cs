using StackExchange.Redis;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add controllers
builder.Services.AddControllers();

// Read from environment variable for Redis server
var redisServer = builder.Configuration.GetValue<string>("REDIS_SERVER") ?? "localhost:6379";   

// Add Redis connection multiplexer as a singleton service
builder.Services.AddSingleton<IConnectionMultiplexer>(ConnectionMultiplexer.Connect(redisServer));
// Config connection pooling of redis
builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>  
{
    var configurationOptions = ConfigurationOptions.Parse(redisServer);
    configurationOptions.AbortOnConnectFail = false;
    configurationOptions.ClientName = "MyRedisClient";   
    configurationOptions.ConnectTimeout = 5000;
    configurationOptions.SyncTimeout = 5000;
    configurationOptions.KeepAlive = 180;
    return ConnectionMultiplexer.Connect(configurationOptions);
});

// Add HttpClient factory
builder.Services.AddHttpClient();

var app = builder.Build();

// Configure the HTTP request pipeline.
// if (app.Environment.IsDevelopment())
// {
    app.UseSwagger();
    app.UseSwaggerUI();
// }

app.UseHttpsRedirection();
app.MapControllers();
app.Run();

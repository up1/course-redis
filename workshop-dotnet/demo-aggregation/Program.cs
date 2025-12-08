using StackExchange.Redis;

public class Program
{
    public static async Task Main(string[] args)
    {
        // NOTE: Replace with your actual Redis connection string
        // Read redis host from environment variable or use default localhost
        string redisHost = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "localhost";
        string redisPort = Environment.GetEnvironmentVariable("REDIS_PORT") ?? "6379";
        string RedisConnString = $"{redisHost}:{redisPort}";
        const string CsvFilePath = "orders.csv";

        // 1. Run the report generator
        var generator = new ReportGenerator(RedisConnString);
        generator.ProcessOrders(CsvFilePath);

        // 2. Verify the data (Optional)
        await VerifyReportData(RedisConnString);

        // 3. Retrieve the Top 10 Spenders
        var retriever = new ReportRetriever(RedisConnString);
        var top10 = await retriever.GetTopSpenders(10);

        Console.WriteLine("\n--- Top 10 Spenders Leaderboard ---");
        for (int i = 0; i < top10.Count; i++)
        {
            Console.WriteLine($"#{i + 1}: User ID {top10[i].UserId} - ${top10[i].TotalSpend:N2}");
        }
    }

    private static async Task VerifyReportData(string connString)
    {
        ConnectionMultiplexer redis = ConnectionMultiplexer.Connect(connString);
        // Ping to ensure connection is established
        var pong = await redis.GetDatabase().PingAsync();
        Console.WriteLine($"Connected to Redis, Ping: {pong.TotalMilliseconds} ms");
        IDatabase db = redis.GetDatabase();

        Console.WriteLine("\n--- Verification ---");

        // Example Daily Check (2025-12-05: 2 orders, 170.99 revenue)
        var dailyHash = await db.HashGetAllAsync("report:daily:2025-12-05");
        Console.WriteLine($"Daily Report 2025-12-05: Orders={dailyHash.First(x => x.Name == "orders").Value}, Revenue={dailyHash.First(x => x.Name == "revenue").Value}");

        // Example Monthly Check (2025-12: 5 orders, 294.49 revenue)
        // (170.99 + 25.50 + 88.00 + 10.00 = 294.49)
        var monthlyHash = await db.HashGetAllAsync("report:monthly:2025-12");
        Console.WriteLine($"Monthly Report 2025-12: Orders={monthlyHash.First(x => x.Name == "orders").Value}, Revenue={monthlyHash.First(x => x.Name == "revenue").Value}");
    }
}
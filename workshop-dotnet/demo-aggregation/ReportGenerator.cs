using StackExchange.Redis;
using CsvHelper;
using System.Globalization;

public class ReportGenerator
{
    private readonly IDatabase _redisDb;
    private const int BatchSize = 5000; // Optimal batch size for pipelining

    public ReportGenerator(string redisConnectionString)
    {
        // Connect to Redis only once
        ConnectionMultiplexer redis = ConnectionMultiplexer.Connect(redisConnectionString);
        _redisDb = redis.GetDatabase();
    }

    public void ProcessOrders(string filePath)
    {
        var orders = ReadCsvFile(filePath);
        Console.WriteLine($"Read {orders.Count} orders from CSV. Starting Redis pipeline...");

        // Execute the report generation
        AggregateOrdersInRedis(orders);

        Console.WriteLine("Redis pipeline completed successfully.");
    }

    // --- Helper to Read CSV ---
    private List<Order> ReadCsvFile(string filePath)
    {
        using var reader = new StreamReader(filePath);
        using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);
        // Ensure the CsvHelper reads the 'timestamp' correctly
        return csv.GetRecords<Order>().ToList();
    }

    // --- Core Redis Pipelining Logic ---
    private void AggregateOrdersInRedis(List<Order> orders)
    {
        // Get an instance of the Redis transaction/pipeline object
        var batch = _redisDb.CreateBatch();
        int commandCount = 0;

        // Key for the Top Spenders Leaderboard
        const string TopSpendersKey = "report:topspenders";

        foreach (var order in orders)
        {
            // 1. Calculate Time Keys
            var dailyKey = GetDailyKey(order.Timestamp);
            var weeklyKey = GetWeeklyKey(order.Timestamp);
            var monthlyKey = GetMonthlyKey(order.Timestamp);

            // 2. Add HASH commands to the batch (pipeline)
            // Daily Report
            batch.HashIncrementAsync(dailyKey, "orders", 1);
            batch.HashIncrementAsync(dailyKey, "revenue", (double)order.Amount);

            // Weekly Report
            batch.HashIncrementAsync(weeklyKey, "orders", 1);
            batch.HashIncrementAsync(weeklyKey, "revenue", (double)order.Amount);

            // Monthly Report
            batch.HashIncrementAsync(monthlyKey, "orders", 1);
            batch.HashIncrementAsync(monthlyKey, "revenue", (double)order.Amount);

            // 3. Sorted Set Update for Top Spenders
            // ZINCRBY Command: Atomically adds the order amount to the user's current score
            // Member is prefixed with 'user:' for clarity/type safety
            var userMember = $"user:{order.UserId}";
            batch.SortedSetIncrementAsync(TopSpendersKey, userMember, (double)order.Amount);

            commandCount += 7; // 7 commands added per order

            // 3. Execute the batch periodically to prevent pipeline overflow
            if (commandCount >= BatchSize)
            {
                batch.Execute();
                commandCount = 0;
                batch = _redisDb.CreateBatch(); // Start a new batch
            }
        }

        // Execute any remaining commands in the final batch
        if (commandCount > 0)
        {
            batch.Execute();
        }
    }

    // --- Key Formatting Helpers ---

    private string GetDailyKey(DateTime dt) => $"report:daily:{dt.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture)}";

    private string GetMonthlyKey(DateTime dt) => $"report:monthly:{dt.ToString("yyyy-MM", CultureInfo.InvariantCulture)}";

    private string GetWeeklyKey(DateTime dt)
    {
        // Use ISO 8601 week numbering: yyyy-Wnn
        // DateTimeFormatInfo.CurrentInfo.Calendar.GetWeekOfYear handles this
        // CalendarWeekRule.FirstDay: Treats Jan 1 as the first day of the first week
        // You might want to adjust CultureInfo for ISO week (Monday start) if required by your locale
        var calendar = CultureInfo.InvariantCulture.Calendar;
        var weekNum = calendar.GetWeekOfYear(dt, CalendarWeekRule.FirstFourDayWeek, DayOfWeek.Monday);
        return $"report:weekly:{dt.Year}-W{weekNum:D2}";
    }
}
using StackExchange.Redis;

public class ReportRetriever
{
    private readonly IDatabase _redisDb;
    private const string TopSpendersKey = "report:topspenders";

    public ReportRetriever(string redisConnectionString)
    {
        ConnectionMultiplexer redis = ConnectionMultiplexer.Connect(redisConnectionString);
        _redisDb = redis.GetDatabase();
    }

    public async Task<List<TopSpender>> GetTopSpenders(int count)
    {
        // ZREVRANGE Command:
        // - key: TopSpendersKey
        // - start: 0 (the highest ranked member)
        // - stop: count - 1 (e.g., 9 for top 10)
        var rankedUsers = await _redisDb.SortedSetRangeByRankWithScoresAsync(
            TopSpendersKey, 
            0, 
            count - 1, 
            StackExchange.Redis.Order.Descending
        );

        var topSpenders = new List<TopSpender>();
        foreach (var entry in rankedUsers)
        {
            // The member value is a RedisValue (e.g., "user:45")
            string userIdString = entry.Element.ToString().Replace("user:", "");
            
            if (int.TryParse(userIdString, out int userId))
            {
                topSpenders.Add(new TopSpender
                {
                    UserId = userId,
                    TotalSpend = (decimal)entry.Score // Convert score back to decimal
                });
            }
        }

        return topSpenders;
    }
}

// Model for the result
public class TopSpender
{
    public int UserId { get; set; }
    public decimal TotalSpend { get; set; }
}
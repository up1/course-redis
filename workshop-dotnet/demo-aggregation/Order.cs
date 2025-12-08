using CsvHelper.Configuration.Attributes;

public class Order
{
    [Name("order_id")]
    public int OrderId { get; set; }

    [Name("user_id")]
    public int UserId { get; set; }

    [Name("amount")]
    public decimal Amount { get; set; } // Use decimal for financial precision

    [Name("timestamp")]
    public DateTime Timestamp { get; set; }
}
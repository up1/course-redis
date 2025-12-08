package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/redis/go-redis/v9"
)

var rdb *redis.Client // Global Redis client

func initRedis() {
	var ctx = context.Background()
	rdb = redis.NewClient(&redis.Options{
		Addr:     "redis:6379", // Redis address
		Password: "",           // No password set
		DB:       0,            // Use default DB
	})

	// Test connection
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	fmt.Println("Successfully connected to Redis!")
}

func main() {
	// Initialize Redis client
	initRedis()
	defer rdb.Close()

	// Initialize sample data
	initData()

}

// Initialize sample data in Redis
func initData() {
	// Add 100,000 emails to the Bloom filter
	start := time.Now()
	for i := 0; i < 100000; i++ {
		email := fmt.Sprintf("user%d@example.com", i)
		err := addEmail("existing_emails", email)
		if err != nil {
			log.Fatalf("Failed to add email to Bloom filter: %v", err)
		}
	}
	elapsed := time.Since(start)
	fmt.Printf("Added 100,000 emails in %s\n", elapsed)

	// Get memory size of redis
	var ctx = context.Background()
	info, err := rdb.Info(ctx, "memory").Result()
	if err != nil {
		log.Fatalf("Failed to get Redis memory info: %v", err)
	}
	fmt.Println("Redis Memory Info:")
	fmt.Println(info)
}

// addEmail adds an email to the Bloom filter
func addEmail(key string, email string) error {
	var ctx = context.Background()
	// BF.ADD command: key, item
	return rdb.Do(ctx, "BF.ADD", key, email).Err()
}

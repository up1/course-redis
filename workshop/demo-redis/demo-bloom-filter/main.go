package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/redis/go-redis/v9"
)

// User struct for data mapping
type User struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

var rdb *redis.Client // Global Redis client

func initRedis() {
	var ctx = context.Background()
	rdb = redis.NewClient(&redis.Options{
		Addr:     "localhost:6379", // Redis address
		Password: "",               // No password set
		DB:       0,                // Use default DB
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

	e := echo.New()

	// Health check endpoint
	e.GET("/health", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})
	// Check email endpoint
	e.GET("/users/:email", checkEmailHandler)

	e.Logger.Fatal(e.Start(":8080"))
}

// Initialize sample data in Redis
func initData() {
	sampleEmails := []string{
		"john.doe@example.com",
		"jane.smith@example.com",
		"alice.johnson@example.com",
		"bob.brown@example.com",
	}

	// Add sample emails to Bloom filter
	bloomFilterKey := "existing_emails"
	for _, email := range sampleEmails {
		err := addEmail(bloomFilterKey, email)
		if err != nil {
			log.Fatalf("Failed to add email to Bloom filter: %v", err)
		}
	}
}

// addEmail adds an email to the Bloom filter
func addEmail(key string, email string) error {
	var ctx = context.Background()
	// BF.ADD command: key, item
	return rdb.Do(ctx, "BF.ADD", key, email).Err()
}

// Check if an email address might exist in the Bloom filter
func checkEmailExists(key string, email string) (bool, error) {
	var ctx = context.Background()
	// BF.EXISTS command: key, item
	result, err := rdb.Do(ctx, "BF.EXISTS", key, email).Result()
	if err != nil {
		return false, err
	}
	fmt.Println(result)
	// Result is 1 if it might exist, 0 if it definitely does not exist
	return result.(bool), nil
}

// Check email endpoint handler
func checkEmailHandler(c echo.Context) error {
	email := c.Param("email")
	exists, err := checkEmailExists("existing_emails", email)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Internal Server Error"})
	}

	user := map[string]interface{}{
		"email":       email,
		"might_exist": exists,
		"checked_at":  time.Now().Format(time.RFC3339),
	}

	return c.JSON(http.StatusOK, user)
}

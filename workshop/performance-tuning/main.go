package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/redis/go-redis/v9"
)

// User struct for data mapping
type User struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

var rdb *redis.Client // Global Redis client

func initRedis() {
	var ctx = context.Background()
	rdb = redis.NewClient(&redis.Options{
		Addr:     "localhost:6379", // Redis address
		Password: "",               // No password set
		DB:       0,                // Use default DB
	})

	// Working with pool settings
	rdb.Options().PoolSize = 200                     // Maximum number of connections
	rdb.Options().MinIdleConns = 100                 // Minimum number of idle connections
	rdb.Options().ConnMaxIdleTime = 5 * time.Minute  // Maximum idle time
	rdb.Options().ConnMaxLifetime = 30 * time.Minute // Maximum lifetime of a connection
	rdb.Options().PoolTimeout = 30 * time.Second     // Maximum wait time for a connection

	// Test connection
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	fmt.Println("Successfully connected to Redis!")
}

//

func main() {

	initRedis()
	defer rdb.Close()

	e := echo.New()

	// Health check endpoint
	e.GET("/health", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})
	// Simple API with database access
	e.GET("/users/:id", getUser)

	e.Logger.Fatal(e.Start(":8080"))
}

// Simple API handler example
func getUser(c echo.Context) error {
	id := c.Param("id")
	var user User

	// 1. Check Redis cache first
	ctx := context.Background()
	cacheKey := fmt.Sprintf("user:%s:name", id)
	cachedName, err := rdb.Get(ctx, cacheKey).Result()
	if err == nil {
		// Cache hit
		userID, _ := strconv.Atoi(id)
		user.ID = userID
		user.Name = cachedName
		return c.JSON(http.StatusOK, user)
	}

	// 2. Cache miss, set default user data (simulate DB access)
	userID, _ := strconv.Atoi(id)
	user = User{
		ID:   userID,
		Name: fmt.Sprintf("User%d", userID),
	}

	// 3. Store in Redis cache for future requests with a TTL of 10 minutes
	err = rdb.Set(ctx, cacheKey, user.Name, 10*time.Minute).Err()
	if err != nil {
		log.Printf("Failed to set cache for user %s: %v", id, err)
	}

	return c.JSON(http.StatusOK, user)
}

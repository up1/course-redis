package main

import (
	"context"
	"demo/handlers"
	"demo/redis"
	"fmt"
	"log"
	"net/http"
)

func main() {
	// Create a new Redis client with connection pooling
	rdb := redis.NewRedisService()

	ctx := context.Background()

	// Test the connection
	pong, err := rdb.Client.Ping(ctx).Result()
	if err != nil {
		fmt.Printf("Error connecting to Redis: %v\n", err)
		return
	}
	fmt.Printf("Connected to Redis: %v\n", pong)
	defer rdb.Client.Close()

	handler := handlers.NewHandler(rdb)
	http.HandleFunc("/set", handler.SetKey)
	http.HandleFunc("/get", handler.GetKey)

	log.Println("Server starting on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}

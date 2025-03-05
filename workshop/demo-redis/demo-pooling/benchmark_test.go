package main

import (
	"bytes"
	"demo/handlers"
	"demo/redis"
	"encoding/json"
	"net/http/httptest"
	"testing"

	"github.com/go-faker/faker/v4"
)

func BenchmarkSetKey(b *testing.B) {
	redisService := redis.NewRedisService()
	handler := handlers.NewHandler(redisService)

	data := handlers.KeyValue{
		Key:   faker.Username(),
		Value: faker.Name(),
	}
	jsonData, _ := json.Marshal(data)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("POST", "/set", bytes.NewBuffer(jsonData))
		w := httptest.NewRecorder()
		handler.SetKey(w, req)
	}
}

func BenchmarkGetKey(b *testing.B) {
	redisService := redis.NewRedisService()
	handler := handlers.NewHandler(redisService)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("GET", "/get?key=test_key", nil)
		w := httptest.NewRecorder()
		handler.GetKey(w, req)
	}
}

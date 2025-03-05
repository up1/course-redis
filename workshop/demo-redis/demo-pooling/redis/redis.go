package redis

import (
	"context"

	"github.com/redis/go-redis/v9"
)

type RedisService struct {
	Client *redis.Client
}

func NewRedisService() *RedisService {
	client := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "",
		DB:       0,
		PoolSize: 1,
	})

	return &RedisService{Client: client}
}

func (s *RedisService) Set(ctx context.Context, key string, value interface{}) error {
	return s.Client.Set(ctx, key, value, 0).Err()
}

func (s *RedisService) Get(ctx context.Context, key string) (string, error) {
	return s.Client.Get(ctx, key).Result()
}

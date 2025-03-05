package handlers

import (
	"demo/redis"
	"encoding/json"
	"net/http"
)

type Handler struct {
	redisService *redis.RedisService
}

type KeyValue struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}

func NewHandler(redisService *redis.RedisService) *Handler {
	return &Handler{redisService: redisService}
}

func (h *Handler) SetKey(w http.ResponseWriter, r *http.Request) {
	var kv KeyValue
	if err := json.NewDecoder(r.Body).Decode(&kv); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err := h.redisService.Set(r.Context(), kv.Key, kv.Value)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func (h *Handler) GetKey(w http.ResponseWriter, r *http.Request) {
	key := r.URL.Query().Get("key")
	if key == "" {
		http.Error(w, "key is required", http.StatusBadRequest)
		return
	}

	value, err := h.redisService.Get(r.Context(), key)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(KeyValue{Key: key, Value: value})
}

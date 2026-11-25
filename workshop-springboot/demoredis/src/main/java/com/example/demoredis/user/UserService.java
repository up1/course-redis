package com.example.demoredis.user;

import java.time.Duration;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import com.example.demoredis.common.InvalidInputException;
import com.example.demoredis.common.UserNotFoundException;

import tools.jackson.databind.ObjectMapper;

@Service
public class UserService {
	private static final Logger log = LoggerFactory.getLogger(UserService.class);

	private final UserRepository repository;
	private final StringRedisTemplate redis;
	private final ObjectMapper mapper;
	private final Duration ttl;
	private final String prefix;

	public UserService(UserRepository repository, StringRedisTemplate redis, ObjectMapper mapper,
			@Value("${app.cache.user-ttl}") Duration ttl,
			@Value("${app.cache.key-prefix}") String prefix) {
		this.repository = repository;
		this.redis = redis;
		this.mapper = mapper;
		this.ttl = ttl;
		this.prefix = prefix;
	}

	/** Endpoint 1: PostgreSQL only. */
	public User getFromDb(String rawId) {
		long id = parseId(rawId);
		return repository.findById(id).orElseThrow(UserNotFoundException::new);
	}

	/** Endpoint 2: Redis first, fall back to PostgreSQL, then populate Redis. */
	public User getWithCache(String rawId) {
		long id = parseId(rawId);
		String key = prefix + id;

		Optional<User> cached = readCache(key);
		if (cached.isPresent()) {
			return cached.get();
		}
		User user = repository.findById(id).orElseThrow(UserNotFoundException::new);
		writeCache(key, user);
		return user;
	}

	private long parseId(String raw) {
		try {
			long id = Long.parseLong(raw);
			if (id <= 0) {
				throw new InvalidInputException();
			}
			return id;
		} catch (NumberFormatException e) {
			throw new InvalidInputException();
		}
	}

	// Redis problems (down / timeout) must not break the API: degrade to PostgreSQL.
	private Optional<User> readCache(String key) {
		try {
			String json = redis.opsForValue().get(key);
			return json == null ? Optional.empty() : Optional.of(mapper.readValue(json, User.class));
		} catch (Exception e) {
			log.warn("Redis read failed for {}: {}", key, e.toString());
			return Optional.empty();
		}
	}

	private void writeCache(String key, User user) {
		try {
			redis.opsForValue().set(key, mapper.writeValueAsString(user), ttl);
		} catch (Exception e) {
			log.warn("Redis write failed for {}: {}", key, e.toString());
		}
	}
}

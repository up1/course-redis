package com.example.demoredis.user;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
public class UserController {
	private final UserService service;

	public UserController(UserService service) {
		this.service = service;
	}

	/** PostgreSQL only */
	@GetMapping("/db/{id}")
	public User getFromDb(@PathVariable String id) {
		return service.getFromDb(id);
	}

	/** Redis + PostgreSQL */
	@GetMapping("/{id}")
	public User getWithCache(@PathVariable String id) {
		return service.getWithCache(id);
	}
}

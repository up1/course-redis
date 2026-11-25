package com.example.demoredis.user;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/** Generates test users directly inside PostgreSQL (single INSERT ... SELECT), only when the table is empty. */
@Component
public class UserDataSeeder implements ApplicationRunner {
	private static final Logger log = LoggerFactory.getLogger(UserDataSeeder.class);

	private final JdbcTemplate jdbc;
	private final int total;

	public UserDataSeeder(JdbcTemplate jdbc, @Value("${app.seed.users}") int total) {
		this.jdbc = jdbc;
		this.total = total;
	}

	@Override
	public void run(ApplicationArguments args) {
		if (total <= 0) {
			return;
		}
		Long count = jdbc.queryForObject("SELECT COUNT(*) FROM users", Long.class);
		if (count != null && count > 0) {
			log.info("users table already has {} rows, skip seeding", count);
			return;
		}
		long start = System.currentTimeMillis();
		log.info("Seeding {} users ...", total);
		jdbc.update("""
				INSERT INTO users (id, name, username, email, phone, website,
				  street, suite, city, zipcode, lat, lng,
				  company_name, catch_phrase, bs)
				SELECT x, 'User ' || x, 'user' || x, 'user' || x || '@example.com',
				  '1-770-' || x, 'user' || x || '.org',
				  'Street ' || x, 'Apt. ' || MOD(x, 1000), 'City ' || MOD(x, 500), LPAD(MOD(x, 100000)::text, 5, '0'),
				  '-37.3159', '81.1496',
				  'Company ' || MOD(x, 10000), 'Multi-layered client-server neural-net', 'harness real-time e-markets'
				FROM generate_series(1, ?::bigint) AS x
				""", total);
		log.info("Seeded {} users in {} ms", total, System.currentTimeMillis() - start);
	}
}

package com.example.demoredis.user;

import jakarta.persistence.Embedded;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/** JPA entity; serialised as-is to JSON (matches the API spec) and stored in Redis. */
@Entity
@Table(name = "users")
public class User {
	@Id
	private Long id;
	private String name;
	private String username;
	private String email;
	@Embedded
	private Address address;
	private String phone;
	private String website;
	@Embedded
	private Company company;

	public Long getId() { return id; }
	public void setId(Long id) { this.id = id; }
	public String getName() { return name; }
	public void setName(String name) { this.name = name; }
	public String getUsername() { return username; }
	public void setUsername(String username) { this.username = username; }
	public String getEmail() { return email; }
	public void setEmail(String email) { this.email = email; }
	public Address getAddress() { return address; }
	public void setAddress(Address address) { this.address = address; }
	public String getPhone() { return phone; }
	public void setPhone(String phone) { this.phone = phone; }
	public String getWebsite() { return website; }
	public void setWebsite(String website) { this.website = website; }
	public Company getCompany() { return company; }
	public void setCompany(Company company) { this.company = company; }
}

package com.example.demoredis.common;

public class UserNotFoundException extends RuntimeException {
	public UserNotFoundException() { super("User not found in system"); }
}

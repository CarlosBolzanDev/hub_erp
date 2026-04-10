package com.example.demo.dto;

import com.example.demo.model.Role;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record UserRequest(
        @NotBlank String name,
        @NotBlank String username,
        @Email @NotBlank String email,
        @NotBlank String password,
        Role role,
        boolean active
) {}

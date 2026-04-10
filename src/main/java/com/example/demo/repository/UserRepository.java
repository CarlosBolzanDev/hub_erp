package com.example.demo.repository;

import com.example.demo.model.AppUser;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<AppUser, Long> {
    Optional<AppUser> findByUsername(String username);
    Page<AppUser> findByNameContainingIgnoreCaseOrUsernameContainingIgnoreCase(String name, String username, Pageable pageable);
}

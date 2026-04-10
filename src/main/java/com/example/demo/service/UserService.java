package com.example.demo.service;

import com.example.demo.dto.UserRequest;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.AppUser;
import com.example.demo.model.Role;
import com.example.demo.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public Page<AppUser> list(String search, Pageable pageable) {
        if (search == null || search.isBlank()) return userRepository.findAll(pageable);
        return userRepository.findByNameContainingIgnoreCaseOrUsernameContainingIgnoreCase(search, search, pageable);
    }

    public AppUser get(Long id) {
        return userRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("Usuário não encontrado"));
    }

    public AppUser create(UserRequest req) {
        AppUser user = new AppUser();
        user.setName(req.name());
        user.setUsername(req.username());
        user.setEmail(req.email());
        user.setPassword(passwordEncoder.encode(req.password()));
        user.setRole(req.role() == null ? Role.USER : req.role());
        user.setActive(req.active());
        return userRepository.save(user);
    }

    public AppUser update(Long id, UserRequest req) {
        AppUser user = get(id);
        user.setName(req.name());
        user.setUsername(req.username());
        user.setEmail(req.email());
        if (req.password() != null && !req.password().isBlank()) {
            user.setPassword(passwordEncoder.encode(req.password()));
        }
        user.setRole(req.role() == null ? user.getRole() : req.role());
        user.setActive(req.active());
        return userRepository.save(user);
    }

    public void delete(Long id) {
        userRepository.delete(get(id));
    }

    public long count() { return userRepository.count(); }
}

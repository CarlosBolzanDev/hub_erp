package com.example.demo.controller;

import com.example.demo.dto.UserRequest;
import com.example.demo.model.Role;
import com.example.demo.service.ActivityLogService;
import com.example.demo.service.UserService;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;

@Controller
@RequestMapping
public class UserController {
    private final UserService userService;
    private final ActivityLogService logService;

    public UserController(UserService userService, ActivityLogService logService) {
        this.userService = userService;
        this.logService = logService;
    }

    @GetMapping("/users")
    public String list(@RequestParam(defaultValue = "") String search,
                       @RequestParam(defaultValue = "0") int page,
                       @RequestParam(defaultValue = "id") String sort,
                       @RequestParam(defaultValue = "asc") String dir,
                       Model model) {
        var pageable = PageRequest.of(page, 10, dir.equalsIgnoreCase("desc") ? Sort.by(sort).descending() : Sort.by(sort).ascending());
        model.addAttribute("users", userService.list(search, pageable));
        model.addAttribute("search", search);
        model.addAttribute("roles", Role.values());
        return "users/list";
    }

    @PostMapping("/users")
    public String create(@Valid @ModelAttribute("form") UserRequest request, BindingResult result, Principal principal) {
        if (result.hasErrors()) return "redirect:/users?error";
        userService.create(request);
        logService.log(principal.getName(), "CREATE_USER", "SUCCESS");
        return "redirect:/users";
    }

    @PostMapping("/users/{id}/delete")
    public String delete(@PathVariable Long id, Principal principal) {
        userService.delete(id);
        logService.log(principal.getName(), "DELETE_USER", "SUCCESS");
        return "redirect:/users";
    }

    @ResponseBody
    @GetMapping("/api/users")
    public Object listApi(@RequestParam(defaultValue = "") String search,
                          @RequestParam(defaultValue = "0") int page,
                          @RequestParam(defaultValue = "10") int size) {
        return userService.list(search, PageRequest.of(page, size));
    }

    @ResponseBody
    @PostMapping("/api/users")
    public ResponseEntity<?> createApi(@Valid @RequestBody UserRequest request, Principal principal) {
        var saved = userService.create(request);
        logService.log(principal.getName(), "CREATE_USER_API", "SUCCESS");
        return ResponseEntity.ok(saved);
    }
}

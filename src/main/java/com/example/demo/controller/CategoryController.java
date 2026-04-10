package com.example.demo.controller;

import com.example.demo.dto.CategoryRequest;
import com.example.demo.service.ActivityLogService;
import com.example.demo.service.CategoryService;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;

@Controller
@RequestMapping
public class CategoryController {
    private final CategoryService categoryService;
    private final ActivityLogService logService;

    public CategoryController(CategoryService categoryService, ActivityLogService logService) {
        this.categoryService = categoryService;
        this.logService = logService;
    }

    @GetMapping("/categories")
    public String list(@RequestParam(defaultValue = "") String search,
                       @RequestParam(defaultValue = "0") int page,
                       Model model) {
        model.addAttribute("categories", categoryService.list(search, PageRequest.of(page, 10, Sort.by("id").descending())));
        return "categories/list";
    }

    @PostMapping("/categories")
    public String create(@Valid CategoryRequest request, Principal principal) {
        categoryService.create(request);
        logService.log(principal.getName(), "CREATE_CATEGORY", "SUCCESS");
        return "redirect:/categories";
    }

    @ResponseBody
    @GetMapping("/api/categories")
    public Object listApi(@RequestParam(defaultValue = "") String search,
                          @RequestParam(defaultValue = "0") int page,
                          @RequestParam(defaultValue = "10") int size) {
        return categoryService.list(search, PageRequest.of(page, size));
    }

    @ResponseBody
    @PostMapping("/api/categories")
    public ResponseEntity<?> createApi(@Valid @RequestBody CategoryRequest request, Principal principal) {
        var saved = categoryService.create(request);
        logService.log(principal.getName(), "CREATE_CATEGORY_API", "SUCCESS");
        return ResponseEntity.ok(saved);
    }
}

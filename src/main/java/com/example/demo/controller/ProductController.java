package com.example.demo.controller;

import com.example.demo.dto.ProductRequest;
import com.example.demo.service.ActivityLogService;
import com.example.demo.service.CategoryService;
import com.example.demo.service.ProductService;
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
public class ProductController {
    private final ProductService productService;
    private final CategoryService categoryService;
    private final ActivityLogService logService;

    public ProductController(ProductService productService, CategoryService categoryService, ActivityLogService logService) {
        this.productService = productService;
        this.categoryService = categoryService;
        this.logService = logService;
    }

    @GetMapping("/products")
    public String list(@RequestParam(defaultValue = "") String search,
                       @RequestParam(defaultValue = "0") int page,
                       Model model) {
        model.addAttribute("products", productService.list(search, PageRequest.of(page, 10, Sort.by("id").descending())));
        model.addAttribute("categories", categoryService.list("", PageRequest.of(0, 100)).getContent());
        return "products/list";
    }

    @PostMapping("/products")
    public String create(@Valid ProductRequest request, Principal principal) {
        productService.create(request);
        logService.log(principal.getName(), "CREATE_PRODUCT", "SUCCESS");
        return "redirect:/products";
    }

    @ResponseBody
    @GetMapping("/api/products")
    public Object listApi(@RequestParam(defaultValue = "") String search,
                          @RequestParam(defaultValue = "0") int page,
                          @RequestParam(defaultValue = "10") int size) {
        return productService.list(search, PageRequest.of(page, size));
    }

    @ResponseBody
    @PostMapping("/api/products")
    public ResponseEntity<?> createApi(@Valid @RequestBody ProductRequest request, Principal principal) {
        var saved = productService.create(request);
        logService.log(principal.getName(), "CREATE_PRODUCT_API", "SUCCESS");
        return ResponseEntity.ok(saved);
    }
}

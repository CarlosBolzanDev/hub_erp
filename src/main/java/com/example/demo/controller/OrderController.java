package com.example.demo.controller;

import com.example.demo.dto.OrderRequest;
import com.example.demo.model.OrderStatus;
import com.example.demo.service.*;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;
import java.time.LocalDate;

@Controller
@RequestMapping
public class OrderController {
    private final OrderService orderService;
    private final UserService userService;
    private final ProductService productService;
    private final ActivityLogService logService;

    public OrderController(OrderService orderService, UserService userService, ProductService productService, ActivityLogService logService) {
        this.orderService = orderService;
        this.userService = userService;
        this.productService = productService;
        this.logService = logService;
    }

    @GetMapping("/orders")
    public String list(@RequestParam(required = false) OrderStatus status,
                       @RequestParam(required = false) String date,
                       @RequestParam(defaultValue = "0") int page,
                       Model model) {
        LocalDate parsed = (date == null || date.isBlank()) ? null : LocalDate.parse(date);
        model.addAttribute("orders", orderService.list(status, parsed, PageRequest.of(page, 10, Sort.by("id").descending())));
        model.addAttribute("users", userService.list("", PageRequest.of(0, 100)).getContent());
        model.addAttribute("products", productService.list("", PageRequest.of(0, 100)).getContent());
        model.addAttribute("statuses", OrderStatus.values());
        return "orders/list";
    }

    @PostMapping("/orders")
    public String create(@Valid OrderRequest request, Principal principal) {
        orderService.create(request);
        logService.log(principal.getName(), "CREATE_ORDER", "SUCCESS");
        return "redirect:/orders";
    }

    @ResponseBody
    @GetMapping("/api/orders")
    public Object listApi(@RequestParam(required = false) OrderStatus status,
                          @RequestParam(required = false) String date,
                          @RequestParam(defaultValue = "0") int page,
                          @RequestParam(defaultValue = "10") int size) {
        LocalDate parsed = (date == null || date.isBlank()) ? null : LocalDate.parse(date);
        return orderService.list(status, parsed, PageRequest.of(page, size));
    }

    @ResponseBody
    @PostMapping("/api/orders")
    public ResponseEntity<?> createApi(@Valid @RequestBody OrderRequest request, Principal principal) {
        var saved = orderService.create(request);
        logService.log(principal.getName(), "CREATE_ORDER_API", "SUCCESS");
        return ResponseEntity.ok(saved);
    }
}

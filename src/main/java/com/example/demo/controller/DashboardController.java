package com.example.demo.controller;

import com.example.demo.service.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class DashboardController {
    private final UserService userService;
    private final ProductService productService;
    private final OrderService orderService;
    private final ActivityLogService logService;
    private final ExternalApiService externalApiService;

    public DashboardController(UserService userService, ProductService productService, OrderService orderService, ActivityLogService logService, ExternalApiService externalApiService) {
        this.userService = userService;
        this.productService = productService;
        this.orderService = orderService;
        this.logService = logService;
        this.externalApiService = externalApiService;
    }

    @GetMapping({"/", "/dashboard"})
    public String dashboard(Model model) {
        model.addAttribute("usersCount", userService.count());
        model.addAttribute("productsCount", productService.count());
        model.addAttribute("ordersCount", orderService.count());
        model.addAttribute("logsCount", logService.list(null, org.springframework.data.domain.PageRequest.of(0, 1)).getTotalElements());
        model.addAttribute("externalStatus", externalApiService.status().get("status"));
        return "dashboard";
    }
}

package com.example.demo.controller;

import com.example.demo.service.ActivityLogService;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class LogsController {
    private final ActivityLogService activityLogService;

    public LogsController(ActivityLogService activityLogService) {
        this.activityLogService = activityLogService;
    }

    @GetMapping("/logs")
    public String list(@RequestParam(defaultValue = "") String search,
                       @RequestParam(defaultValue = "0") int page,
                       Model model) {
        model.addAttribute("logs", activityLogService.list(search, PageRequest.of(page, 20, Sort.by("id").descending())));
        return "logs/list";
    }
}

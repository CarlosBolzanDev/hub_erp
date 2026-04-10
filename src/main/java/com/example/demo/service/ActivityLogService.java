package com.example.demo.service;

import com.example.demo.model.ActivityLog;
import com.example.demo.repository.ActivityLogRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class ActivityLogService {
    private final ActivityLogRepository activityLogRepository;

    public ActivityLogService(ActivityLogRepository activityLogRepository) {
        this.activityLogRepository = activityLogRepository;
    }

    public void log(String username, String operation, String result) {
        activityLogRepository.save(new ActivityLog(username, operation, result));
    }

    public Page<ActivityLog> list(String search, Pageable pageable) {
        if (search == null || search.isBlank()) {
            return activityLogRepository.findAll(pageable);
        }
        return activityLogRepository.findByUsernameContainingIgnoreCase(search, pageable);
    }
}

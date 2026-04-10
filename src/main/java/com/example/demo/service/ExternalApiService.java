package com.example.demo.service;

import com.example.demo.client.ExternalApiClient;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class ExternalApiService {
    private final ExternalApiClient client;

    public ExternalApiService(ExternalApiClient client) {
        this.client = client;
    }

    public Map<String, Object> status() {
        return client.getHealth();
    }
}

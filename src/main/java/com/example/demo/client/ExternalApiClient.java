package com.example.demo.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Component
public class ExternalApiClient {
    private final RestClient restClient = RestClient.builder().build();
    private final boolean mockEnabled;

    public ExternalApiClient(@Value("${app.external-api.mock-enabled:true}") boolean mockEnabled) {
        this.mockEnabled = mockEnabled;
    }

    public Map<String, Object> getHealth() {
        if (mockEnabled) {
            return Map.of("status", "MOCK_OK", "provider", "MockProvider", "latencyMs", 42);
        }
        return restClient.get()
                .uri("https://api.github.com")
                .retrieve()
                .body(Map.class);
    }
}

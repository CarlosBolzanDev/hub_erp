package com.example.demo.repository;

import com.example.demo.model.CustomerOrder;
import com.example.demo.model.OrderStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;

public interface OrderRepository extends JpaRepository<CustomerOrder, Long> {
    Page<CustomerOrder> findByStatus(OrderStatus status, Pageable pageable);
    Page<CustomerOrder> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end, Pageable pageable);
}

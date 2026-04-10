package com.example.demo.service;

import com.example.demo.dto.OrderRequest;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.CustomerOrder;
import com.example.demo.model.OrderStatus;
import com.example.demo.repository.OrderRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;

@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final UserService userService;
    private final ProductService productService;

    public OrderService(OrderRepository orderRepository, UserService userService, ProductService productService) {
        this.orderRepository = orderRepository;
        this.userService = userService;
        this.productService = productService;
    }

    public Page<CustomerOrder> list(OrderStatus status, LocalDate date, Pageable pageable) {
        if (status != null) return orderRepository.findByStatus(status, pageable);
        if (date != null) return orderRepository.findByCreatedAtBetween(date.atStartOfDay(), date.plusDays(1).atStartOfDay(), pageable);
        return orderRepository.findAll(pageable);
    }

    public CustomerOrder get(Long id) {
        return orderRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("Pedido não encontrado"));
    }

    public CustomerOrder create(OrderRequest req) {
        CustomerOrder o = new CustomerOrder();
        o.setUser(userService.get(req.userId()));
        o.setProduct(productService.get(req.productId()));
        o.setQuantity(req.quantity());
        o.setStatus(req.status() == null ? OrderStatus.NEW : req.status());
        o.setTotalValue(o.getProduct().getPrice().multiply(BigDecimal.valueOf(req.quantity())));
        return orderRepository.save(o);
    }

    public CustomerOrder update(Long id, OrderRequest req) {
        CustomerOrder o = get(id);
        o.setUser(userService.get(req.userId()));
        o.setProduct(productService.get(req.productId()));
        o.setQuantity(req.quantity());
        o.setStatus(req.status() == null ? o.getStatus() : req.status());
        o.setTotalValue(o.getProduct().getPrice().multiply(BigDecimal.valueOf(req.quantity())));
        return orderRepository.save(o);
    }

    public void delete(Long id) { orderRepository.delete(get(id)); }
    public long count() { return orderRepository.count(); }
}

package com.example.demo.config;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
public class DataSeeder implements CommandLineRunner {
    private final UserRepository userRepository;
    private final CategoryRepository categoryRepository;
    private final ProductRepository productRepository;
    private final OrderRepository orderRepository;
    private final ActivityLogRepository activityLogRepository;
    private final PasswordEncoder passwordEncoder;

    public DataSeeder(UserRepository userRepository,
                      CategoryRepository categoryRepository,
                      ProductRepository productRepository,
                      OrderRepository orderRepository,
                      ActivityLogRepository activityLogRepository,
                      PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.categoryRepository = categoryRepository;
        this.productRepository = productRepository;
        this.orderRepository = orderRepository;
        this.activityLogRepository = activityLogRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        if (userRepository.count() > 0) return;

        AppUser admin = new AppUser();
        admin.setName("Administrador");
        admin.setUsername("admin");
        admin.setEmail("admin@hub.local");
        admin.setPassword(passwordEncoder.encode("admin123"));
        admin.setRole(Role.ADMIN);
        userRepository.save(admin);

        AppUser user = new AppUser();
        user.setName("Usuário Teste");
        user.setUsername("user");
        user.setEmail("user@hub.local");
        user.setPassword(passwordEncoder.encode("user123"));
        user.setRole(Role.USER);
        userRepository.save(user);

        Category c1 = new Category();
        c1.setName("Eletrônicos");
        c1.setDescription("Produtos eletrônicos");
        categoryRepository.save(c1);

        Product p = new Product();
        p.setName("Notebook Exemplo");
        p.setSku("NB-001");
        p.setPrice(new BigDecimal("4500.00"));
        p.setStock(15);
        p.setCategory(c1);
        productRepository.save(p);

        CustomerOrder order = new CustomerOrder();
        order.setUser(user);
        order.setProduct(p);
        order.setQuantity(1);
        order.setStatus(OrderStatus.NEW);
        order.setTotalValue(p.getPrice());
        orderRepository.save(order);

        activityLogRepository.save(new ActivityLog("system", "SEED", "Base inicial criada"));
    }
}

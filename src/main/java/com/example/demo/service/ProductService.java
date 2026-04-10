package com.example.demo.service;

import com.example.demo.dto.ProductRequest;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class ProductService {
    private final ProductRepository productRepository;
    private final CategoryService categoryService;

    public ProductService(ProductRepository productRepository, CategoryService categoryService) {
        this.productRepository = productRepository;
        this.categoryService = categoryService;
    }

    public Page<Product> list(String search, Pageable pageable) {
        if (search == null || search.isBlank()) return productRepository.findAll(pageable);
        return productRepository.findByNameContainingIgnoreCase(search, pageable);
    }

    public Product get(Long id) {
        return productRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("Produto não encontrado"));
    }

    public Product create(ProductRequest req) {
        Product p = new Product();
        p.setName(req.name());
        p.setSku(req.sku());
        p.setPrice(req.price());
        p.setStock(req.stock());
        p.setCategory(categoryService.get(req.categoryId()));
        return productRepository.save(p);
    }

    public Product update(Long id, ProductRequest req) {
        Product p = get(id);
        p.setName(req.name());
        p.setSku(req.sku());
        p.setPrice(req.price());
        p.setStock(req.stock());
        p.setCategory(categoryService.get(req.categoryId()));
        return productRepository.save(p);
    }

    public void delete(Long id) { productRepository.delete(get(id)); }
    public long count() { return productRepository.count(); }
}

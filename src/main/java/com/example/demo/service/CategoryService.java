package com.example.demo.service;

import com.example.demo.dto.CategoryRequest;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.Category;
import com.example.demo.repository.CategoryRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class CategoryService {
    private final CategoryRepository categoryRepository;

    public CategoryService(CategoryRepository categoryRepository) {
        this.categoryRepository = categoryRepository;
    }

    public Page<Category> list(String search, Pageable pageable) {
        if (search == null || search.isBlank()) return categoryRepository.findAll(pageable);
        return categoryRepository.findByNameContainingIgnoreCase(search, pageable);
    }

    public Category get(Long id) {
        return categoryRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("Categoria não encontrada"));
    }

    public Category create(CategoryRequest req) {
        Category category = new Category();
        category.setName(req.name());
        category.setDescription(req.description());
        return categoryRepository.save(category);
    }

    public Category update(Long id, CategoryRequest req) {
        Category c = get(id);
        c.setName(req.name());
        c.setDescription(req.description());
        return categoryRepository.save(c);
    }

    public void delete(Long id) { categoryRepository.delete(get(id)); }
    public long count() { return categoryRepository.count(); }
}

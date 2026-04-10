package com.example.demo.service;

import com.example.demo.exception.BusinessException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

@Service
public class FileStorageService {

    @Value("${app.upload.dir:uploads}")
    private String uploadDir;

    public String store(MultipartFile file) {
        if (file.isEmpty()) throw new BusinessException("Arquivo vazio");
        if (file.getSize() > 2_000_000) throw new BusinessException("Arquivo excede 2MB");
        String name = file.getOriginalFilename() == null ? "arquivo.bin" : file.getOriginalFilename();
        if (!(name.endsWith(".png") || name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".csv"))) {
            throw new BusinessException("Apenas PNG/JPG/CSV são permitidos");
        }

        try {
            Path dir = Path.of(uploadDir);
            Files.createDirectories(dir);
            Path target = dir.resolve(System.currentTimeMillis() + "-" + name);
            Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
            return target.toString();
        } catch (IOException e) {
            throw new BusinessException("Erro ao salvar arquivo");
        }
    }
}

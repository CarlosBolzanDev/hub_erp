package com.example.demo.controller;

import com.example.demo.service.ExportService;
import com.example.demo.service.ExternalApiService;
import com.example.demo.service.FileStorageService;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@Controller
@RequestMapping
public class SystemController {
    private final FileStorageService fileStorageService;
    private final ExportService exportService;
    private final ExternalApiService externalApiService;

    public SystemController(FileStorageService fileStorageService, ExportService exportService, ExternalApiService externalApiService) {
        this.fileStorageService = fileStorageService;
        this.exportService = exportService;
        this.externalApiService = externalApiService;
    }

    @PostMapping("/api/upload")
    @ResponseBody
    public ResponseEntity<?> upload(@RequestParam("file") MultipartFile file) {
        return ResponseEntity.ok(java.util.Map.of("path", fileStorageService.store(file)));
    }

    @GetMapping("/api/export/products.csv")
    public ResponseEntity<ByteArrayResource> exportCsv() throws Exception {
        byte[] data = exportService.exportProductsCsv();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=products.csv")
                .contentType(MediaType.parseMediaType("text/csv"))
                .body(new ByteArrayResource(data));
    }

    @GetMapping("/api/export/report.pdf")
    public ResponseEntity<ByteArrayResource> exportPdf() throws Exception {
        byte[] data = exportService.exportSimplePdf();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=report.pdf")
                .contentType(MediaType.APPLICATION_PDF)
                .body(new ByteArrayResource(data));
    }

    @GetMapping("/api/external/status")
    @ResponseBody
    public Object externalStatus() {
        return externalApiService.status();
    }

    @GetMapping("/api/test/slow")
    @ResponseBody
    public Object slow() throws InterruptedException {
        Thread.sleep(3000);
        return java.util.Map.of("message", "Resposta lenta simulada (3s)");
    }

    @GetMapping("/api/test/fail")
    @ResponseBody
    public Object fail() {
        throw new RuntimeException("Falha simulada");
    }
}

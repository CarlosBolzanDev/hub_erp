package com.example.demo.service;

import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.List;

@Service
public class ExportService {
    private final ProductRepository productRepository;

    public ExportService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public byte[] exportProductsCsv() throws IOException {
        List<Product> products = productRepository.findAll();
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try (CSVPrinter printer = new CSVPrinter(new OutputStreamWriter(out, StandardCharsets.UTF_8),
                CSVFormat.DEFAULT.withHeader("ID", "Nome", "SKU", "Preço", "Estoque"))) {
            for (Product p : products) {
                printer.printRecord(p.getId(), p.getName(), p.getSku(), p.getPrice(), p.getStock());
            }
        }
        return out.toByteArray();
    }

    public byte[] exportSimplePdf() throws IOException {
        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage();
            document.addPage(page);
            try (PDPageContentStream content = new PDPageContentStream(document, page)) {
                content.beginText();
                content.setFont(PDType1Font.HELVETICA_BOLD, 16);
                content.newLineAtOffset(50, 750);
                content.showText("Relatório simples - Hub ERP");
                content.setFont(PDType1Font.HELVETICA, 12);
                content.newLineAtOffset(0, -25);
                content.showText("Total de produtos: " + productRepository.count());
                content.endText();
            }
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            document.save(out);
            return out.toByteArray();
        }
    }
}

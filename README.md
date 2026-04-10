# Hub ERP - Projeto exemplo completo (Java + Spring Boot)

## Stack
- Java 21
- Spring Boot (Web, Thymeleaf, Data JPA, Security, Validation)
- H2 em memória
- Swagger/OpenAPI
- Maven
- JUnit 5

## Como executar
```bash
mvn spring-boot:run
```
Acesse:
- App: http://localhost:8080
- Login: `admin` / `admin123`
- H2 Console: http://localhost:8080/h2-console
- Swagger: http://localhost:8080/swagger-ui/index.html

## Funcionalidades principais
1. Login/logout com sessão Spring Security.
2. Dashboard com métricas (usuários, produtos, pedidos, logs e status API externa).
3. CRUD (web + endpoints REST) de usuários, categorias, produtos e pedidos.
4. Busca/filtros/paginação por parâmetros de URL.
5. Integração externa via `ExternalApiClient` com modo mock configurável.
6. Upload de imagem/CSV com validação de tamanho e extensão.
7. Exportação de produtos em CSV e relatório simples em PDF.
8. Logs/auditoria no banco e logs de aplicação em arquivo `logs/hub-erp.log`.
9. Configuração por ambiente (`application.properties`, `application-dev.properties`, `application-test.properties`).
10. Páginas de erro personalizadas (403, 404, 500).
11. Endpoints de teste para lentidão e falha (`/api/test/slow`, `/api/test/fail`).

## Endpoints úteis
- `GET /api/users`
- `POST /api/users`
- `GET /api/categories`
- `POST /api/categories`
- `GET /api/products`
- `POST /api/products`
- `GET /api/orders`
- `POST /api/orders`
- `POST /api/upload`
- `GET /api/export/products.csv`
- `GET /api/export/report.pdf`
- `GET /api/external/status`
- `GET /api/test/slow`
- `GET /api/test/fail`

## Perfis
- `dev` (padrão)
- `test` (usado em testes)

## Estrutura
- `controller` rotas web e REST
- `service` regras de negócio
- `repository` persistência JPA
- `model` entidades
- `dto` entrada de dados
- `config` segurança, CORS e seed
- `exception` tratamento centralizado

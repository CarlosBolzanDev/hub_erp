# Hub ERP Imobiliária Offline

Sistema web local para cadastro de imóveis e controle financeiro, feito com HTML/CSS/JavaScript, Node.js/Express e SQLite. Não depende de serviços externos em tempo de execução: após instalar as dependências, roda offline no computador da imobiliária.

## Funcionalidades

- Dashboard com indicadores de imóveis, recebidos, aberto, parcelas em atraso e painel por imóvel.
- Cadastro, edição, exclusão e impressão de ficha de imóveis.
- Proprietários vinculados aos imóveis.
- Controle financeiro principal por imóvel com saldo, total pago e percentual quitado calculados automaticamente.
- Registro e exclusão de pagamentos com validação de saldo.
- Histórico de alterações financeiras e pagamentos com responsável `Sistema`.
- Busca rápida, filtros por tipo/finalidade/status/situação financeira e paginação.
- Relatórios em CSV e PDF: imóveis, financeiro, pagamentos e resumo geral.

## Requisitos

- Node.js 18 ou superior.
- npm.

## Instalação e execução local

```bash
npm install
npm run init-db
npm run seed # opcional
npm start
```

Acesse: <http://localhost:3000>

## Scripts

- `npm start`: inicia o servidor local Express.
- `npm run init-db`: cria/atualiza o banco SQLite em `data/imobiliaria.sqlite` usando `database/schema.sql`.
- `npm run seed`: insere um imóvel de demonstração se o banco estiver vazio.
- `npm test`: executa testes automatizados com `node:test`.

## Estrutura

```text
backend/
  controllers/     Regras HTTP e respostas da API
  routes/          Rotas REST
  services/        Validações e cálculo financeiro
  server.js        Servidor Express

database/
  schema.sql       SQL completo das tabelas, chaves e índices
  init.js          Script de criação do banco
  db.js            Conexão SQLite local
  seed.js          Dados opcionais de demonstração

public/
  index.html       Aplicação frontend offline
  css/styles.css   Layout responsivo corporativo
  js/app.js        Telas, chamadas à API, máscaras simples e notificações
```

## API principal

- `GET /api/dashboard`
- `GET /api/imoveis`
- `POST /api/imoveis`
- `GET /api/imoveis/:id`
- `PUT /api/imoveis/:id`
- `DELETE /api/imoveis/:id`
- `POST /api/imoveis/:imovelId/pagamentos`
- `PUT /api/pagamentos/:id`
- `DELETE /api/pagamentos/:id`
- `GET /api/relatorios/:type.csv`
- `GET /api/relatorios/:type.pdf`

## Banco de dados

O SQL completo está em `database/schema.sql` e cria as tabelas mínimas exigidas:

- `proprietarios`
- `imoveis`
- `financeiro_imovel`
- `pagamentos`
- `historico_alteracoes`

Todas têm `id`, `created_at` e `updated_at`, com relacionamentos e chaves estrangeiras adequadas.

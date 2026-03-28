# Hub ERP Local (HTML/CSS/JS)

Aplicação SPA local-first para gestão de produtos, kits, descrições, reviews, vendas, frete, sincronização e configurações.

## Como executar localmente

1. Abra a pasta em um servidor local simples.
2. Opções:
   - VS Code + Live Server (Open with Live Server no `index.html`)
   - Python: `python3 -m http.server 5500`
3. Acesse `http://localhost:5500`.

## Arquitetura

- `assets/js/app.js`: bootstrap e eventos globais.
- `assets/js/router.js`: navegação hash-based sem reload.
- `assets/js/state.js`: estado global e preferências locais.
- `assets/js/api.js`: camada mock preparada para backend futuro.
- `assets/js/modules/*`: telas por domínio.
- `assets/js/components/*`: UI reutilizável.
- `assets/js/services/*`: regra de negócio/acesso a dados.

## Próximo passo (backend local)

Substituir funções de `api.js` por chamadas reais para API local/SQLite e manter as interfaces dos services.

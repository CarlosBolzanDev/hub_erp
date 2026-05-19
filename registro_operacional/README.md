# Registro Operacional de Decisões e Evidências

Aplicativo desktop local-first para gestão de **Ocorrências** com ciclo de vida, timeline, anexos, links, RACI, busca FTS5 e exportação.

## Instalação
```bash
pip install -e .[dev]
```

## Executar
```bash
python -m registro_operacional.app.main
```

## Fluxos principais
- Nova ocorrência (status inicial: **Aberta**)
- Abrir ocorrência (muda para **Em andamento**)
- Finalizar ocorrência (exige resultado final)
- Reabrir ocorrência (via serviço)
- Colar print (clipboard) na ocorrência
- Anexar arquivos e links
- Consultar timeline e aba RACI
- Exportar JSON + CSV + PDF

## Status suportados
- Aberta
- Em andamento
- Pendente
- Finalizada
- Reaberta

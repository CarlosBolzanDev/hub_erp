# NFE_ORGANIZER

Aplicação desktop Python 3.11+ para monitorar uma pasta de entrada, classificar XMLs de NF-e, renomear pelo número da nota e mover para subpastas de processamento.

## Executar

```bash
pip install -r requirements.txt
python app.py
```

## Estrutura

- `entrada/`: pasta monitorada.
- `processados/`: destino com categorias `SAIDA`, `DEVOLUCAO`, `TRANSFERENCIA`, `ESTORNO_CREDITO` e `DESCONHECIDOS`.
- `logs/processamento.log`: histórico de processamento.
- `config/configuracoes.json`: caminhos persistidos pela interface.

## Regras de prioridade

1. `ESTORNO_CREDITO`
2. `DEVOLUCAO`
3. `TRANSFERENCIA`
4. `SAIDA`
5. `DESCONHECIDO`

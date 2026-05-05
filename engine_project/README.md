# Generic Python Runtime Engine

## 1. O que é a engine
Runtime genérico para executar scripts Python com API interna padronizada, suporte a modo **headless** e modo **GUI**. O objetivo final é distribuição em EXE autossuficiente (sem Python no cliente).

## 2. Diagnóstico do bug anterior
Antes desta refatoração, `Engine.__init__()` criava `MainWindow` imediatamente e `start()` sempre chamava `mainloop()`. Isso forçava abertura da interface mesmo quando a intenção era apenas rodar scripts automaticamente.

## 3. Como abrir no modo desenvolvimento
```bash
cd engine_project
python runtime_entry.py  # padrão: GUI
python runtime_entry.py --mode gui
```
Ou headless:
```bash
python runtime_entry.py --mode headless
```

## 4. Como gerar o EXE
### Recomendação
Use **onedir** para runtime com scripts/plugins externos (facilita atualização e troubleshooting).

```bash
pyinstaller --noconfirm build.spec
```
Ou use:
```bash
build.bat
```

## 5. Como adicionar scripts `.py` pela interface
1. Abrir com `--mode gui`.
2. Clicar em **Adicionar scripts .py**.
3. Selecionar arquivos.
4. Scripts aparecem na lista.

## 6. Como executar/parar scripts
- **Iniciar** reinicializa com segurança o script selecionado (shutdown + initialize) para sempre gerar efeito visível em log.
- **Parar** chama `shutdown` do script selecionado.
- **Recarregar selecionados** recompõe módulos carregados.
- Sem scripts selecionados/carregados, a engine registra aviso claro em log.

## 7. Como salvar e recarregar seleção
- **Salvar seleção** persiste em `configs/settings.json`.
- Em Configurações, habilite **autoload_selected** para execução automática no headless startup.

## 8. Comunicação script ↔ engine (Engine API)
Contrato disponível em `register(engine_api)`:
- `register_service(name, service)`
- `get_service(name)`
- `emit_event(name, payload=None)`
- `on_event(name, callback)`
- `log(message, level="INFO")`
- `execute_script(path)`
- `load_selected_scripts()`
- `shutdown_script(name)`
- `reload_script(name)`

> Scripts devem ser independentes da UI (não assumir Tkinter/controles visuais).

## 9. Interface mínima obrigatória do script
```python
def register(engine_api):
    ...

def initialize():
    ...

def shutdown():
    ...
```

## 10. Exemplo
Veja `app/scripts/sample_script.py`.

## 11. Estrutura
```text
engine_project/
├── runtime_entry.py
├── build.spec
├── build.bat
├── installer.iss
├── requirements.txt
├── app/
│   ├── core/
│   ├── ui/
│   ├── scripts/
│   ├── assets/
│   └── runtime/
├── configs/
└── README.md
```

## 12. Estratégia de instalador
Use `installer.iss` (Inno Setup) para entregar:
- executável
- configs
- assets
- bibliotecas empacotadas pelo PyInstaller

Sem necessidade de Python instalado localmente.

## 13. Dependências externas de scripts
Se scripts exigirem bibliotecas de terceiros, inclua essas dependências no ambiente de build da engine e reconstrua o EXE para embutir tudo no pacote final.

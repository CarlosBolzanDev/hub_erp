# Generic Python Runtime Engine

## 1) O que é a engine
Uma engine desktop genérica (Tkinter) para selecionar manualmente scripts `.py`, carregar/executar com isolamento de erro e distribuir como EXE autossuficiente (PyInstaller), sem exigir Python instalado no cliente.

## 2) Como abrir a engine no modo desenvolvimento
```bash
cd engine_project
python runtime_entry.py
```

## 3) Como gerar o EXE
### OneDir
```bash
pyinstaller --noconfirm --windowed --name GenericRuntime \
  --add-data "configs;configs" \
  --add-data "app/assets;app/assets" \
  runtime_entry.py
```
### OneFile
```bash
pyinstaller --noconfirm --onefile --windowed --name GenericRuntime \
  --add-data "configs;configs" \
  --add-data "app/assets;app/assets" \
  runtime_entry.py
```

## 4) Como adicionar scripts `.py` pela interface
1. Abra o runtime.
2. Clique em **Adicionar scripts .py**.
3. Selecione um ou mais arquivos Python.
4. Eles passam a aparecer na lista de scripts registrados.

## 5) Como executar e parar scripts
- Selecione um item da lista.
- Clique em **Iniciar** para chamar `initialize()`.
- Clique em **Parar** para chamar `shutdown()`.
- Clique em **Recarregar selecionados** para recarregar módulos já registrados.

## 6) Como salvar e recarregar a seleção
- Clique em **Salvar seleção** para persistir os caminhos em `configs/settings.json`.
- Opcionalmente marque **Auto carregar scripts salvos ao iniciar** nas configurações.

## 7) Como um programa/script deve comunicar com a engine
No `register(engine_api)`, use os métodos:
- `register_service(name, service)`
- `get_service(name)`
- `emit_event(name, payload=None)`
- `on_event(name, callback)`
- `log(message, level)`
- `execute_script(path)`
- `load_selected_scripts()`
- `shutdown_script(name)`
- `reload_script(name)`

## 8) Interface mínima obrigatória de um script
```python
def register(engine_api):
    ...

def initialize():
    ...

def shutdown():
    ...
```

## 9) Exemplos de uso
Veja `app/scripts/sample_script.py` para exemplo de:
- log via API;
- emissão de evento interno.

## 10) Estrutura do projeto
```text
engine_project/
├── runtime_entry.py
├── app/
│   ├── core/
│   ├── ui/
│   ├── scripts/
│   ├── assets/
│   └── runtime/
├── configs/
│   └── settings.json
└── README.md
```

## Observações de empacotamento
`ResourceManager` detecta `sys._MEIPASS` em modo empacotado e grava logs/dados em `runtime_data/` (diretório atual).

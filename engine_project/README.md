# Generic Python Runtime Engine (Tkinter + EXE)

Engine genérica para carregar e executar scripts Python (`.py`) dinamicamente com interface gráfica Tkinter e empacotamento final em EXE autossuficiente.

## Estrutura

```text
engine_project/
├── runtime_entry.py
├── app/
│   ├── core/
│   │   ├── engine.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── script_loader.py
│   │   ├── resource_manager.py
│   │   └── event_bus.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── panels.py
│   │   └── widgets.py
│   ├── scripts/
│   │   └── sample_script.py
│   ├── assets/
│   └── runtime/
├── configs/
│   └── settings.json
└── README.md
```

## Como funciona

1. Você desenvolve a engine em Python.
2. Empacota a engine com PyInstaller.
3. O EXE vira o runtime distribuível.
4. O runtime carrega scripts/plugins de `app/scripts` (ou caminho configurado).
5. Usuário final roda apenas o EXE, sem instalar Python.

## Interface mínima esperada de scripts

Cada script deve implementar:

- `register(engine)`
- `initialize()`
- `shutdown()`

## Execução em desenvolvimento

```bash
cd engine_project
python runtime_entry.py
```

## Build EXE com PyInstaller

### OneDir

```bash
pyinstaller --noconfirm --windowed --name GenericRuntime \
  --add-data "configs;configs" \
  --add-data "app/scripts;app/scripts" \
  --add-data "app/assets;app/assets" \
  runtime_entry.py
```

### OneFile

```bash
pyinstaller --noconfirm --onefile --windowed --name GenericRuntime \
  --add-data "configs;configs" \
  --add-data "app/scripts;app/scripts" \
  --add-data "app/assets;app/assets" \
  runtime_entry.py
```

## Observações de runtime empacotado

- O `ResourceManager` detecta `sys._MEIPASS` para resolver recursos dentro do bundle.
- Logs e dados de execução são gravados em `runtime_data/` no diretório atual.
- Um script com erro não derruba o runtime: a falha é registrada em log e os demais continuam.

## Expansão futura sugerida

- Assinatura/versionamento de plugins.
- Sandboxing de scripts por subprocesso.
- Catálogo remoto de plugins.
- Theme manager mais completo.

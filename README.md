# Engine Portátil de Scripts Python

Esta pasta contém uma engine Windows com GUI própria para localizar, selecionar e executar scripts `.py` externos sob demanda. A engine não cria scripts de exemplo e espera que os scripts reais sejam copiados para `engine/Scripts/`.

## Arquitetura

A engine é modular para separar interface, execução, persistência e integração com runtime portátil:

```text
engine/
├── python/                 # Copie aqui o Python embeddable package para Windows
├── libs/                   # Dependências locais adicionais, se houver
├── Scripts/                # Scripts externos do usuário
├── config/settings.json    # Seleção persistente e preferências
├── logs/                   # Logs gerados em runtime
├── core/                   # Loader, executor, runtime, config e logging
├── ui/                     # Janela Tkinter, lista e painel de logs
├── utils/                  # Validação e utilidades de arquivos
└── engine_gui.py           # Ponto de entrada
```

Fluxo principal:

1. `engine_gui.py` prepara os caminhos portáteis e inicia a GUI.
2. `RuntimeBridge` adiciona `libs/`, `Scripts/` e `python/` ao `sys.path`.
3. `ScriptLoader` lista apenas `.py` válidos dentro de `Scripts/`.
4. A GUI permite marcar scripts, salvar a seleção em JSON e executar sob demanda.
5. `ScriptExecutor` carrega cada script com `importlib`, procura `run(context)` ou `main(context)` e captura erros sem derrubar a interface.
6. `LoggerManager` grava em `engine/logs/engine.log` e envia mensagens para o painel de logs.

## Contrato dos scripts externos

Cada script copiado para `engine/Scripts/` deve expor uma das funções abaixo:

```python
def run(context):
    return {"status": "ok", "message": "executado com sucesso"}
```

ou:

```python
def main(context):
    return {"status": "ok", "message": "executado com sucesso"}
```

O `context` recebido pelo script contém:

- `paths`: caminhos de `base_dir`, `scripts_dir`, `libs_dir`, `config_dir`, `logs_dir` e `script_path`.
- `settings`: seleção atual, opções de execução e argumentos padrão.
- `arguments`: texto do campo de argumentos extras da GUI.
- `logger`: logger filho para o script.

## Runtime embutido para Windows

1. Baixe o **Windows embeddable package** da versão desejada em <https://www.python.org/downloads/windows/>.
2. Extraia todo o conteúdo em `engine/python/`, mantendo `python.exe`, `python3.dll`, `python3x._pth` e demais arquivos do pacote.
3. Edite `engine/python/python3x._pth` e inclua os caminhos locais usados pela engine, por exemplo:

```text
python3x.zip
.
..\libs
..\Scripts
..
import site
```

> Observação: a GUI usa Tkinter por não exigir PySide/PyQt. Em algumas versões do embeddable package, os arquivos Tcl/Tk podem precisar ser copiados do instalador oficial da mesma versão do Python para dentro do runtime portátil. Ao gerar um `.exe` com PyInstaller, esses arquivos normalmente são coletados pelo build quando o ambiente de build possui Tkinter funcional.

## Executar em desenvolvimento

No Linux/macOS/Windows com Python local disponível:

```bash
python engine/engine_gui.py
```

No Windows portátil, depois de preencher `engine/python/`:

```bat
engine\python\python.exe engine\engine_gui.py
```

## Gerar executável Windows

O build deve ser feito em uma máquina Windows. O PC final não precisa ter Python instalado.

1. Prepare um ambiente de build com Python da mesma versão do embeddable runtime.
2. Instale o PyInstaller **apenas na máquina de build**:

```bat
py -m pip install pyinstaller
```

3. Gere o executável incluindo pastas portáteis:

```bat
py -m PyInstaller --noconsole --name EngineScripts --add-data "engine\config;config" --add-data "engine\libs;libs" --add-data "engine\Scripts;Scripts" --add-data "engine\python;python" engine\engine_gui.py
```

4. Distribua a pasta `dist\EngineScripts\` para o PC final.
5. Copie os scripts reais para `dist\EngineScripts\Scripts\` quando necessário.

## Configuração persistente

`engine/config/settings.json` armazena:

- `selected_scripts`: scripts marcados na GUI.
- `scripts_folder`: pasta de scripts, padrão `Scripts`.
- `execution_options`: opções como `stop_on_error`.
- `default_arguments`: argumentos padrão exibidos no campo da GUI.

## Logs

A engine grava logs em `engine/logs/engine.log` durante execução local. No executável gerado, o log fica dentro da pasta `logs/` ao lado da aplicação distribuída.

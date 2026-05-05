# Engine Windows Portátil para Scripts Python Externos

Esta engine fornece uma GUI Windows para cadastrar manualmente scripts `.py` externos, salvar esses caminhos em um manifesto local e executá-los sob demanda usando o Python embutido distribuído junto com a engine. Ela **não assume** que os scripts ficam em uma pasta fixa da engine: os arquivos podem estar em qualquer caminho local, removível ou de rede acessível no PC final.

## Arquitetura

```text
engine/
├── python/                         # Python embeddable package para Windows
├── libs/                           # Bibliotecas locais carregadas pelo runtime embutido
├── config/
│   └── engine_manifest.json        # Manifesto dos scripts cadastrados
├── logs/                           # Arquivos de log da engine
├── core/
│   ├── script_loader.py            # Registro/validação por caminho externo
│   ├── script_executor.py          # Import dinâmico e execução run/main
│   ├── runtime_bridge.py           # Preparação do runtime portátil
│   ├── config_manager.py           # Leitura/escrita do manifesto JSON
│   └── logger_manager.py           # Logging em arquivo e GUI
├── ui/
│   ├── main_window.py              # Janela principal e eventos
│   ├── script_manager_widget.py    # Lista de scripts, ativo/status/caminho
│   └── log_viewer.py               # Painel de logs em tempo real
└── engine_gui.py                   # Ponto de entrada
```

Decisões técnicas principais:

- A GUI usa Tkinter para reduzir dependências e facilitar distribuição portátil.
- Scripts são cadastrados por caminho salvo no manifesto, não por varredura de uma pasta fixa.
- O carregamento usa `importlib.util.spec_from_file_location`, permitindo importar módulos a partir de qualquer arquivo `.py` acessível.
- O manifesto fica em `engine/config/engine_manifest.json` e armazena nome exibido, caminho, ativo/inativo, status de validação, última execução e opções.
- O runtime adiciona `engine/libs/` e `engine/python/` ao `sys.path`; dependências extras devem ser distribuídas junto com a engine, sem depender de `pip` no PC final.

## Fluxo de uso

1. O usuário abre a engine.
2. A engine prepara o ambiente portátil e carrega `config/engine_manifest.json`.
3. A GUI mostra os scripts já cadastrados, mesmo que estejam fora da pasta da engine.
4. O usuário clica em **Adicionar script** e escolhe qualquer arquivo `.py` acessível.
5. O script é validado, recebe um nome amigável e é salvo no manifesto.
6. O usuário ativa/desativa scripts pela coluna **Ativo**.
7. **Executar selecionados** executa todos os scripts ativos.
8. **Executar um script** executa apenas a linha selecionada.
9. Logs e erros aparecem na interface e em `logs/engine.log`.

## Contrato dos scripts externos

Preferencialmente, cada script deve expor:

```python
def run(context):
    ...
```

ou:

```python
def main(context):
    ...
```

A engine também tenta executar scripts legados com `run()` ou `main()` sem parâmetros quando a assinatura permitir.

O `context` enviado para scripts com contexto contém:

- `paths.base_dir`, `paths.libs_dir`, `paths.config_dir`, `paths.logs_dir`, `paths.script_path` e `paths.script_dir`.
- `config.execution_options` e `config.default_arguments`.
- `arguments`, com o texto informado no campo de argumentos extras.
- `logger`, um logger filho específico do script.
- `script_name`, `script_path` e `script_id`.

## Manifesto JSON

Exemplo estrutural sem scripts cadastrados:

```json
{
  "default_arguments": "",
  "execution_options": {
    "stop_on_error": false
  },
  "scripts": []
}
```

Cada script adicionado pela GUI é persistido como um item com `id`, `display_name`, `path`, `enabled`, `validation_status` e `last_execution`.

## Runtime embutido para Windows

1. Baixe o **Windows embeddable package** da versão desejada em <https://www.python.org/downloads/windows/>.
2. Extraia todo o conteúdo em `engine/python/`, mantendo `python.exe`, `python3.dll`, `python3x._pth` e os demais arquivos.
3. Edite `engine/python/python3x._pth` para incluir as libs locais e a pasta da engine:

```text
python3x.zip
.
..\libs
..
import site
```

> Tkinter pode exigir arquivos Tcl/Tk compatíveis com a versão do Python usada. Em builds PyInstaller feitos em uma máquina com Tkinter funcional, esses arquivos normalmente são coletados automaticamente.

## Executar em desenvolvimento

```bash
python engine/engine_gui.py
```

## Executar com runtime embutido no Windows

```bat
engine\python\python.exe engine\engine_gui.py
```

Também há um atalho batch:

```bat
engine\run_engine.bat
```

## Gerar executável Windows

O build deve ser feito em uma máquina Windows. O PC final não precisa ter Python instalado.

1. Prepare uma máquina de build com Python compatível com o runtime embutido.
2. Instale o PyInstaller apenas na máquina de build:

```bat
py -m pip install pyinstaller
```

3. Gere o executável incluindo `config`, `libs` e `python`:

```bat
py -m PyInstaller --noconsole --name EngineScripts --add-data "engine\config;config" --add-data "engine\libs;libs" --add-data "engine\python;python" engine\engine_gui.py
```

4. Distribua `dist\EngineScripts\` para o PC final.
5. Os scripts externos podem permanecer onde estiverem, desde que os caminhos salvos no manifesto sejam acessíveis no PC final.

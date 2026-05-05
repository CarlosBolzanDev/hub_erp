# Windows Python Embedded Script Launcher

Este projeto entrega uma arquitetura Windows portátil em que o ponto de entrada é um único `main.exe`, construído em **C# WinForms**, e a execução dos scripts é feita por uma engine Python local baseada no **Python embeddable package**. A stack escolhida é adequada para Windows porque o WinForms gera uma aplicação desktop simples, estável e familiar para distribuição, enquanto o Python embeddable permite executar `.py` externos sem instalar Python no computador final.

## Arquitetura entregue

```text
project/
├─ main.exe                         # gerado em dist/project após o build
├─ src/WindowsPythonLauncher/        # código-fonte do app Windows
├─ engine/
│  ├─ python/                        # receberá o Python embeddable package
│  ├─ libs/                          # dependências Python locais opcionais
│  ├─ engine_launcher.py             # CLI chamada pelo main.exe sob demanda
│  ├─ script_loader.py               # carregamento dinâmico de módulos .py
│  ├─ config_manager.py              # leitura/escrita de JSON local
│  ├─ logger.py                      # logs da engine e dos scripts
│  └─ runtime_bridge.py              # ponte entre UI, contexto e scripts
├─ Scripts/
│  ├─ layout.py                      # exemplo com run(context)
│  ├─ dashboard.py                   # exemplo com main(context)
│  └─ executavel.py                  # exemplo com estado local
├─ config/
│  ├─ settings.json
│  └─ selected_scripts.json
├─ logs/
├─ assets/
└─ tools/
   ├─ setup-python-embeddable.ps1
   └─ build-main.ps1
```

## Como funciona

1. O `main.exe` inicia a interface gráfica e procura automaticamente arquivos `*.py` na pasta `Scripts/`.
2. O desenvolvedor marca/desmarca scripts e salva a seleção em `config/selected_scripts.json`.
3. Ao executar um script, o `main.exe` cria `config/run_context.json` com caminhos, argumentos, configurações e scripts selecionados.
4. O `main.exe` chama `engine/python/python.exe engine/engine_launcher.py` apenas durante a execução solicitada.
5. A engine carrega o arquivo `.py` dinamicamente, detecta `run(context)` ou `main(context)`, executa a função e captura retorno/exceções.
6. Logs são escritos em `logs/ui-YYYYMMDD.log` pela interface e em `logs/main-YYYYMMDD.log` pela engine.

Essa abordagem não mantém uma engine separada aberta continuamente. Cada execução é sob demanda e isolada logicamente por um novo processo Python.

## Interface gráfica

A interface WinForms inclui:

- lista de scripts com checkbox;
- botão **Salvar seleção**;
- botão **Executar script**;
- botão **Recarregar scripts**;
- campo de argumentos opcionais;
- área de logs em tempo real;
- indicação de sucesso, aviso ou erro.

## Contrato dos scripts

Cada arquivo em `Scripts/` deve exportar `run(context)` ou `main(context)`:

```python
def run(context):
    logger = context["logger"]
    logger.info("Executando script")
    return {
        "status": "ok",
        "message": "Script executado com sucesso"
    }
```

Se nenhuma função compatível existir, a engine retorna erro claro: `O script deve exportar uma função run(context) ou main(context).`

## Contexto disponível para os scripts

O objeto `context` é um dicionário Python com dados como:

- `app_root`: pasta raiz do aplicativo;
- `script_name`: nome do script selecionado;
- `script_path`: caminho completo do script;
- `scripts_dir`: pasta de scripts;
- `config_dir`: pasta de configuração;
- `logs_dir`: pasta de logs;
- `args`: texto bruto digitado no campo de argumentos;
- `args_list`: argumentos quebrados em lista;
- `settings`: conteúdo de `config/settings.json`;
- `selected_scripts`: lista salva de scripts marcados;
- `logger`: objeto com métodos `info`, `warning`, `error` e `exception`;
- `config_manager`: helper para ler e escrever JSON local.

## Preparar o Python embeddable package

Em uma máquina Windows com PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File tools/setup-python-embeddable.ps1 -Version 3.12.4 -Architecture amd64
```

O script baixa o pacote oficial `python-3.12.4-embed-amd64.zip`, extrai em `engine/python/` e ajusta o arquivo `python312._pth` para habilitar `import site` e a pasta `engine/libs`.

### Dependências Python locais

Para bibliotecas puramente Python, copie os pacotes para `engine/libs/`. Para dependências com DLLs/extensões nativas, mantenha os arquivos exigidos dentro do pacote final e teste em uma máquina limpa.

## Build do `main.exe`

Pré-requisitos de build:

- Windows 10/11 ou Windows Server compatível;
- .NET 8 SDK instalado apenas na máquina de build;
- Python embeddable package preparado em `engine/python/`.

Gerar o pacote final:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build-main.ps1
```

O resultado fica em:

```text
dist/project/main.exe
```

O pacote `dist/project/` deve conter também `engine/`, `Scripts/`, `config/`, `logs/` e `assets/`.

## Distribuição para outro PC

Copie a pasta inteira `dist/project/` para outra máquina Windows compatível. O usuário final executa apenas:

```text
main.exe
```

Não é necessário instalar Python no PC final. Para adicionar ou atualizar scripts, copie novos `.py` para `Scripts/` e use **Recarregar scripts** na interface.

## Tratamento de erros

A aplicação trata os principais cenários:

- runtime embutido ausente (`engine/python/python.exe` não encontrado);
- launcher da engine ausente;
- script não encontrado;
- arquivo sem contrato `run(context)` ou `main(context)`;
- exceções lançadas pelo script, com traceback gravado em log;
- retorno não serializável, convertido para texto seguro.

## Evolução futura

A arquitetura já separa interface, engine, configuração, logging e carregamento dinâmico. Para evoluir, é possível adicionar:

- fila de execução;
- comunicação entre scripts via arquivos JSON, SQLite ou message bus local;
- perfis de configuração;
- execução em paralelo;
- permissões por script;
- empacotamento MSI/MSIX.

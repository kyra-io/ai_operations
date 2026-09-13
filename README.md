# AI OP Copilot

CLI Python para consultar modelos Mistral. Autor: Pedro Santo.

## Preparação

Instala o [uv](https://docs.astral.sh/uv/getting-started/installation/).
Na raiz do repositório, sincroniza o ambiente com as versões do lockfile:

```sh
uv sync --locked
```

O uv gere o Python 3.13 indicado em `.python-version` e o ambiente `.venv`.
Não é necessário ativar o ambiente manualmente.

Cria um ficheiro `.env` na raiz, ou utiliza o existente, com os teus valores:

```dotenv
MISTRAL_API_KEY=<a tua chave de API>
MISTRAL_MODEL=<identificador do modelo a utilizar>
```

O ficheiro `.env` está excluído do Git.

## Execução

```sh
uv run ai-op-copilot
```

Também podes executar `uv run python -m ai_op_copilot`.
A CLI pede uma pergunta e envia-a à API do Mistral.

## Dependências

O projeto utiliza exclusivamente o fluxo de projetos do uv:

```sh
uv add <pacote>
uv remove <pacote>
uv lock
uv sync --locked
```

As dependências diretas estão no `pyproject.toml`; o `uv.lock` fixa também
as dependências transitivas. Guarda ambos no Git. As versões diretas atuais
continuam fixas; para as atualizar, utiliza `uv add <pacote>==<nova-versão>`.

## Estrutura

```text
.python-version
pyproject.toml
uv.lock
src/ai_op_copilot/
    __init__.py
    __main__.py
    cli.py
    mistral/
        __init__.py
        mistral.py
        mistral_types.py
```

Para gerar as distribuições em `dist/`, executa `uv build`.

## Estado atual

A migração para uv organiza a instalação e a entrada da CLI. A integração
continua com problemas conhecidos: `latency_ms` recebe uma string vazia
apesar de exigir um inteiro, `completion_tokens` copia os tokens do prompt,
e as exceções da API ainda não são tratadas. Estes pontos precisam de correção
para completar o fluxo de resposta com sucesso.

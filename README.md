# netshoes_marketplace_copilot

Agente KAM Virtual para sellers Long Tail da Netshoes: diagnostica gargalos no nível de SKU
filho, simula impacto financeiro de ajuste de preço e devolve no máximo três recomendações
priorizadas.

A constituição do projeto (regras de negócio inegociáveis, stack travada, arquitetura) está em
`openspec/project.md`. A change que criou esta fundação está em
`openspec/changes/001-core-contracts-and-skeleton/`.

## Requisitos

- Python 3.11–3.13
- Dependências de `pyproject.toml`

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Execução offline (sem credencial GCP)

O backend `mock` lê as fixtures CSV locais e não faz nenhuma chamada de rede. É o caminho
usado pelos testes.

```bash
cp .env.example .env
# no .env, ajuste:
#   DW_BACKEND=mock
```

As fixtures vivem em `tests/fixtures/` e **estão no `.gitignore`** — não são versionadas. Para
regenerá-las:

```bash
.venv/bin/python scripts/generate_synthetic_data.py
```

## Subir a API

```bash
DW_BACKEND=mock .venv/bin/uvicorn kam_agent.api.app:app --reload
```

Endpoints:

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/health` | Backends em uso e dependências indisponíveis |
| `POST` | `/chat` | Conversa com o copiloto |

O `POST /chat` recebe `{"mensagem": "..."}`. O seller **nunca** vem do corpo: use o header
`X-Seller-Id` (ou `X-Sessao` para reaproveitar uma sessão).

```bash
curl -s http://127.0.0.1:8000/health

curl -s -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Seller-Id: 10024' \
  -d '{"mensagem": "quero ver meu diagnostico"}'
```

Com `DW_BACKEND=bigquery`, o `/health` responde `status: degradado` nomeando o adapter
BigQuery, que é um stub explícito nesta change e levanta `NotImplementedError`.

## Rodar os testes

```bash
.venv/bin/pytest
```

- Testes unitários: `tests/unit/` — não dependem das fixtures; constroem CSVs sintéticos em
  diretório temporário.
- Teste de integração: `tests/integration/` — usa as fixtures reais e **se auto-pula** quando
  elas estão ausentes (caso do CI).

## Qualidade

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

## Arquitetura

```
src/kam_agent/
├── config.py        # Settings (pydantic-settings), backends validados
├── domain/          # enums, modelos Pydantic, guardrails puros, exceções
├── ports/           # SellerDataPort, SessionMemoryPort (Protocol)
├── adapters/        # schema_mapping, mock CSV, BigQuery stub, memória, factory
├── tools/           # ferramentas determinísticas (seller do estado, não do prompt)
├── agents/          # estado, roteador, grafo LangGraph
└── api/             # schemas, dependências, rotas, app
```

O pacote `domain/` não importa `fastapi`, `langgraph`, `google.cloud` nem `pydantic_settings`
— há teste dedicado garantindo esse isolamento.
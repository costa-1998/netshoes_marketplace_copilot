# Proposal

## Why

O repositório tem a constituição (`openspec/project.md`), as fixtures locais (`seller_master.csv` e `seller_sku_sales.csv`) e um `pyproject.toml` com a stack travada — mas nenhuma linha de código de domínio: `src/kam_agent/` tem apenas seis `__init__.py` vazios. Sem contratos estáveis, o primeiro agente LangGraph, query BigQuery ou endpoint FastAPI congela decisões de schema por acidente, e os guardrails inegociáveis (trava 1P, Buy Box preço-vs-logística, ruptura em Curva A, rentabilidade mínima, isolamento multi-tenant, Top 3) acabam implementados em prompt de LLM, onde não são auditáveis nem testáveis.

Esta change estabelece a fundação executável: modelos Pydantic v2 no grão de SKU filho, guardrails como funções puras, portas e adapters, memória de sessão e um esqueleto de API e de grafo que roda e passa em testes sem credencial GCP.

## What Changes

- **Novo `src/kam_agent/config.py`**: `Settings` via `pydantic-settings` espelhando `.env.example`, com validação fechada de `DW_BACKEND` e `MEMORY_BACKEND` na inicialização.
- **Novo `src/kam_agent/domain/`**: enums, modelos Pydantic v2 do cadastro do seller (`SellerMaster`) e do registro diário por SKU filho (`SkuFilhoDailyMetrics`), exceções e os guardrails como funções puras — zero dependência de GCP, FastAPI ou LangGraph.
- **Novo `src/kam_agent/ports/`**: `SellerDataPort` e `SessionMemoryPort` como `Protocol` com `runtime_checkable`.
- **Novo `src/kam_agent/adapters/`**: mapeamento explícito coluna → campo-do-domínio, `CsvMockSellerAdapter` (backend `DW_BACKEND=mock`), `BigQuerySellerAdapter` como stub que falha alto, `InMemorySessionAdapter` com TTL e uma factory que resolve as portas a partir de `Settings`.
- **Novo `src/kam_agent/tools/`**: ferramentas determinísticas que recebem `id_seller` do estado, nunca do prompt.
- **Novo `src/kam_agent/agents/`**: `StateGraph` mínimo com estado tipado, roteador determinístico e nó de especialista substituto (sem chamada a LLM).
- **Novo `src/kam_agent/api/`**: app FastAPI com `GET /health` e `POST /chat`, injeção de dependência, middleware de contexto de sessão e handler global de erros sem vazamento.
- **Testes**: unitários de guardrail, mapeamento e normalização; contrato dos adapters; isolamento de camada do domínio; smoke e integração da API.

Fora de escopo nesta change: chamada real ao Vertex AI, execução de SQL em BigQuery, renderização de card PNG com Playwright, integração com WhatsApp, autenticação real de seller e o motor completo de simulação de preço.

## Capabilities

### New Capabilities

- `seller-data`: contrato de leitura do cadastro do seller (`seller_master.csv`) e de performance diária por SKU filho (`seller_sku_sales.csv`), adapters mock e BigQuery stub, e o mapeamento explícito entre as colunas do schema consolidado e o modelo de domínio — incluindo coerção segura de nulos (ex.: `preco_1p`) e booleanos.
- `session-memory`: contrato de memória de sessão com expiração por TTL, pronto para troca por Redis sem alterar chamadores.
- `guardrails`: os modelos de análise e as regras inegociáveis que decidem o que pode ser recomendado — trava 1P (`tem_1p`), priorização preço-vs-logística na Buy Box (`delta_preco` vs. `delta_prazo`), bloqueio por ruptura em Curva A (`categoria_curva == "A"` e `cobertura <= 3.0`), diagnóstico de abandono de funil/cancelamentos, piso de rentabilidade (`rentabilidade > 0.05`) na simulação de preço, isolamento por `id_seller` e limite de Top 3.
- `agent-orchestration`: grafo de orquestração com estado tipado, roteamento determinístico por intenção e contrato de ferramentas que recebem `id_seller` do estado.
- `chat-api`: superfície HTTP com health check que nomeia dependência indisponível, endpoint de conversa e resolução de portas por configuração.

### Modified Capabilities

Nenhuma — `openspec/specs/` está vazio.

## Impact

- **Código**: cria `src/kam_agent/{config.py,domain,ports,adapters,tools,agents,api}/`; os `__init__.py` existentes permanecem.
- **Dependências**: usa apenas o que já está em `pyproject.toml`. Nada de `pandas` — as fixtures são CSV simples e o `csv` da stdlib basta.
- **Configuração**: `.env.example` passa a ser a referência de `Settings`; nenhuma variável nova obrigatória.
- **Dados**: consome `tests/fixtures/seller_sku_sales.csv` (1.050 linhas, 36 colunas, grão `data + id_seller + sku_filho`, 14 dias entre 2026-11-14 e 2026-11-27) e `tests/fixtures/seller_master.csv` (5 sellers, 9 colunas) como backend mock. **As fixtures estão no `.gitignore`** (`tests/fixtures/*.csv`), então o CI não as tem: os testes unitários constroem CSVs sintéticos em diretório temporário (`tmp_path`) e o teste de integração se auto-pula quando as fixtures locais estão ausentes.
- **Sistemas externos**: nenhum acesso real a BigQuery ou Vertex AI; o adapter BigQuery é stub e falha de forma explícita.
- **Riscos e premissas conhecidas**:
  - As fixtures sintéticas contêm intencionalmente 140 registros diários de cauda longa com venda zero (`unidades_vendidas = 0`, `receita_faturada = 0.0`, `taxa_conversao = 0.0`) para validar a ausência de divisão por zero nos cálculos de conversão e rentabilidade.
  - O funil é monotônico na fixture (`sessoes >= cliques >= adicao_ao_carrinho >= adicao_de_informacoes_de_envio >= adicao_de_pagamento >= compras_faturadas`) em 100% das linhas, garantido pelo gerador. Como a fixture não contém queda real entre etapas, o diagnóstico de atrito de checkout é testado com dados sintéticos controlados.

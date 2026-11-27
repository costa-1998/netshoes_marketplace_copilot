# Constituição do Projeto: Agente KAM Virtual — Netshoes Marketplace

## 1. Propósito e Escopo
Construir um **Key Account Manager (KAM) Virtual** focado em sellers **Long Tail** da Netshoes, atuando via canal conversacional (WhatsApp / API) para:
1. Diagnosticar gargalos no nível de **SKU Filho**: ruptura de estoque na Curva A, perda de Buy Box (preço vs. prazo/frete), trava 1P, abandono nas etapas do funil (PDP → carrinho → envio → pagamento) e cancelamentos.
2. Simular o impacto financeiro de ajustes de preço competitivo (`preco_por` vs. `winner_avg_price`) garantindo sustentabilidade de rentabilidade (`rentabilidade > 0.05`).
3. Entregar no máximo **Top 3 recomendações priorizadas** por impacto financeiro, acompanhadas de cards visuais otimizados para mobile.

---

## 2. Stack Tecnológica e Infraestrutura (Travada)
* **Linguagem:** Python 3.13 (`requires-python = ">=3.11,<3.14"`).
* **API & Contratos:** FastAPI + Pydantic v2 (`pydantic-settings` para configuração).
* **Orquestração Multi-Agente:** LangGraph (`StateGraph`).
* **Provedor LLM:** Google Cloud Vertex AI (`langchain-google-vertexai` / `google-genai`) via Application Default Credentials (ADC).
  * Orquestrador: `gemini-2.5-pro`
  * Subagentes Especialistas: `gemini-2.5-flash`
* **Data Warehouse & Fixtures:** Google BigQuery (`google-cloud-bigquery`) com adaptador local determinístico (`DW_BACKEND=mock` lendo `tests/fixtures/seller_master.csv` e `tests/fixtures/seller_sku_sales.csv`).
* **Validação SQL Dinâmica:** `sqlglot` (AST parser).
* **Renderização Visual:** Jinja2 + Playwright (Chromium headless) gerando PNGs otimizados para WhatsApp.
* **Memória de Sessão:** Interface `SessionMemoryPort` iniciando com adaptador `InMemorySessionAdapter` (pronto para migração futura para Redis).
* **Qualidade e Testes:** `ruff` (linter/formatter) e `pytest` + `pytest-asyncio`.

---

## 3. Fonte de Verdade de Dados e Schemas
Todo modelo Pydantic, tool determinística e query SQL deve seguir estritamente os dois contratos acoplados em `tests/fixtures/`:
* **`seller_master.csv` (9 colunas):** `id_seller`, `nome_seller`, `nota_reputacao`, `contato_nome`, `contato_telefone`, `contato_email`, `rentabilidade`, `taxa_conversao`, `percentual_de_comissao`.
* **`seller_sku_sales.csv` (36 colunas, grão `data + id_seller + sku_filho`):**
  * Identificação: `data`, `id_seller`, `sku_pai`, `sku_filho`, `nome_produto`, `categoria_do_produto`, `categoria_curva` (`A`, `B` ou `C` via Pareto 80-95-100).
  * Estoque & Giro: `vmd`, `estoque`, `cobertura` (dias).
  * Receita & Margem: `unidades_vendidas`, `receita_captada`, `receita_faturada`, `percentual_de_comissao`, `valor_de_comissao`, `margem`, `rentabilidade`.
  * Preço & Competitividade: `preco_de`, `preco_por`, `preco_1p`, `delta_preco` (`preco_por - winner_avg_price`), `prazo_medio_envio`, `delta_prazo` (`prazo_medio_envio - winner_avg_prazo`), `custo_frete`, `tem_1p`, `buybox_win_rate`, `winner_avg_price`, `winner_avg_prazo`.
  * Funil Completo: `sessoes`, `cliques`, `adicao_ao_carrinho`, `adicao_de_informacoes_de_envio`, `adicao_de_pagamento`, `compras_faturadas`, `cancelamentos`, `taxa_conversao` (`compras_faturadas / cliques`).

---

## 4. Arquitetura Hexagonal (Clean Architecture)
Todo código em `src/kam_agent/` deve respeitar o isolamento de camadas:
* `domain/`: Modelos Pydantic (`SellerMaster`, `SkuFilhoDailyMetrics`, `DiagnosticFinding`, `PriceSimulationResult`, `RecommendationCard`), regras de cálculo financeiro e exceções de domínio (zero dependência de GCP, FastAPI ou LangGraph).
* `ports/`: Interfaces abstratas (`ABC` / `Protocol`) para acesso a dados (`SellerDataPort`) e memória (`SessionMemoryPort`).
* `adapters/`: Implementações concretas (`CsvMockSellerAdapter`, `BigQuerySellerAdapter`, `InMemorySessionAdapter`).
* `tools/`: Ferramentas determinísticas chamadas pelos agentes (recebem `id_seller` injetado pelo estado, nunca pelo prompt).
* `agents/`: Grafo LangGraph, roteador e subagentes especialistas (Diagnóstico, Simulador de Preço e Margem, Sintetizador Top 3).
* `api/`: Endpoints FastAPI, injeção de dependências e middlewares.

---

## 5. Regras de Negócio Inegociáveis (Guardrails)
1. **Granularidade Obrigatória por SKU Filho:** Toda análise de ruptura, preço, prazo, funil e Buy Box deve ocorrer no nível de `sku_filho`. Nunca recomendar ações agregadas apenas no `sku_pai`.
2. **Trava Anti-Canibalização 1P (`tem_1p`):** Se `tem_1p == True` no `sku_filho`, é **proibido** sugerir redução de preço ou ação agressiva para disputar Buy Box contra a própria Netshoes (`preco_1p`). O diagnóstico deve apenas sinalizar a presença do 1P naquela variação e focar nos demais SKUs filho sem 1P.
3. **Priorização de Buy Box (Preço vs. Prazo/Frete):**
   * Se `delta_preco <= 0` e `buybox_win_rate < 0.50` com `delta_prazo > 0`, o diagnóstico deve apontar **gargalo logístico (prazo de envio / frete)**, jamais redução de preço.
   * Só sugerir redução de preço quando `delta_preco > 0` e houver margem sustentável.
4. **Proteção contra Ruptura na Curva A:** Se `categoria_curva == "A"` e `cobertura <= 3.0`, bloquear qualquer sugestão de redução de preço para aceleração de giro e priorizar alerta urgente de reposição de estoque.
5. **Diagnóstico de Abandono de Funil e Cancelamento:**
   * Queda acentuada entre `adicao_ao_carrinho` → `adicao_de_informacoes_de_envio` → `adicao_de_pagamento` indica atrito de frete/prazo no checkout.
   * Taxa de `cancelamentos / compras_faturadas > 0.15` dispara alerta operacional de ruptura fantasma ou atraso de expedição.
6. **Trava de Rentabilidade na Simulação de Preço:** Qualquer simulação de redução de preço (`preco_por` → `winner_avg_price`) deve recalcular a margem líquida considerando o `percentual_de_comissao` vigente e validar que a `rentabilidade` projetada permaneça **acima de 5% (`> 0.05`)**.
7. **Isolamento Multi-Tenant (`id_seller`) e Limite Cognitivo:**
   * Nenhuma consulta (CSV ou SQL via `sqlglot`) pode executar sem o filtro explícito `id_seller = :id_seller` vindo do contexto autenticado da sessão.
   * Toda resposta final ao seller deve consolidar no máximo **3 recomendações priorizadas** (Top 3) por impacto financeiro estimado.

---

## 6. Fluxo Git e Governança SDD
* **Branch Protegida:** Nunca realizar commits ou push diretamente na branch `main`.
* **Isolamento por Change:** Toda nova feature/change deve ser desenvolvida em uma branch dedicada no padrão `feat/<numero-da-change>-<nome-curto>` (ex: `feat/001-core-contracts`).
* **Critério de Conclusão:** Uma change só é considerada pronta após passar por `/opsx:verify` (ou `/openspec-verify-change`), `ruff check .`, `pytest`, arquivamento da change e revisão via Pull Request na `main`.
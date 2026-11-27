# Design

## Context

Ver `proposal.md` — Why. Restrições concretas levantadas na inspeção do repositório, que moldam as decisões abaixo:

**Estado do código.** `src/kam_agent/` contém apenas seis `__init__.py` vazios (`domain`, `ports`, `tools`, `agents`, `api` — falta `adapters`). `pyproject.toml` já declara toda a stack travada. `tests/unit/test_env_smoke.py` só verifica que os pacotes importam. Baseline: `pytest` passa (1 teste); `ruff check .` falha com 32 erros, **todos em `scripts/generate_synthetic_data.py`** (E501), arquivo não versionado.

**Estado dos dados.** `tests/fixtures/seller_sku_sales.csv` tem 1.050 linhas e 36 colunas, com grão `(data, id_seller, sku_filho)` e zero duplicatas nessa chave:

- 5 sellers, 14 dias (2026-11-14 a 2026-11-27), 15 SKUs filho por seller, 67 SKUs pai.
- `categoria_curva`: A=462, B=280, C=308. `tem_1p`: true=140, false=910.
- **Todas as colunas de guardrail têm dado**: `buybox_win_rate` ∈ [0.05, 0.90], `delta_preco`, `delta_prazo`, `cobertura` ∈ [0.1, 2400.0], `rentabilidade` ∈ [0.2004, 0.3501].
- `preco_1p` é preenchido **exatamente** quando `tem_1p == true` (140 linhas) e vazio caso contrário.
- 140 linhas têm `unidades_vendidas == 0` e `rentabilidade` preenchida — zero é valor legítimo, não ausência.
- Invariantes que **se sustentam**: `delta_preco = preco_por − winner_avg_price`, `delta_prazo = prazo_medio_envio − winner_avg_prazo`, `taxa_conversao = compras_faturadas / cliques`, `rentabilidade = margem / receita_faturada`, `receita_faturada = preco_por × unidades_vendidas`, e o funil completo é monotônico (`sessoes >= cliques >= adicao_ao_carrinho >= adicao_de_informacoes_de_envio >= adicao_de_pagamento >= compras_faturadas`) em 100% das linhas.
- Invariantes que **quebram**: `receita_captada ≠ preco_de × unidades_vendidas` em 910 linhas, e `preco_de ≠ preco_por` em 100% das linhas (preço "de" promocional). `receita_captada` é exposta como dado bruto, sem derivar preço dela.
- `flag_estoque_fim_dia = 'LOJA ONLINE'`, `qtd_estoque_total_fim_dia`, `faixa_de_cobertura_fim_dia`, `prazo_visto_pond_fim_dia` **não existem** nesta fixture — a fixture não é a view; é um recorte simplificado com nomes de coluna próprios.

**As fixtures estão no `.gitignore`** (`tests/fixtures/*.csv`, linha 226) e não são versionadas. O CI não as terá.

**Divergência entre a fixture e a view.** A fixture usa nomes próximos do domínio (`preco_por`, `delta_preco`, `tem_1p`, `winner_avg_price`); a view `copiloto_seller_sku_diario` descrita no dicionário usa nomes de origem (`preco_por_fim_dia`, `gap_preco_vs_menor_sku_pct`, `flag_1p_ativo_sku`, `menor_preco_por_sku_dia`). O mapeamento precisa cobrir os dois vocabulários — o adapter mock lê a fixture, o adapter BigQuery lerá a view.

**Decisão de escopo já tomada com o usuário:** contratos + esqueleto executável, com campos sem origem mapeados para `Optional` e o guardrail correspondente degradando para "não avaliável".

## Goals / Non-Goals

**Goals:**

- Um modelo de domínio que represente honestamente o que a origem entrega, sem inventar dado.
- Guardrails como funções puras, testáveis com dados sintéticos, retornando três estados distintos: aprovado, bloqueado, não avaliável.
- Um caminho executável de ponta a ponta (`POST /chat` → grafo → porta de dados → resposta) que roda offline, sem credencial GCP, e que é o mesmo caminho que a implementação real usará.
- Um único ponto de mapeamento schema-da-view → domínio, para que uma mudança de view seja uma mudança localizada.

**Non-Goals:**

- Chamada real a Vertex AI, execução de SQL em BigQuery, renderização de card e integração WhatsApp.
- Autenticação real de seller. O esqueleto assume um `seller_id` já autenticado e injetado; o mecanismo de autenticação é uma change futura.
- Corrigir a fixture além do funil: `preco_de ≠ preco_por` é propriedade do dado sintético (preço "de" promocional), não bug a consertar no código.
- Simulador financeiro completo de rebate de comissão — removido da constituição vigente, que agora exige apenas o piso de rentabilidade na simulação de preço.

## Decisions

### D1. Granularidade é um campo do registro, não uma premissa

`PerformanceSKU` carrega `granularidade: Literal["sku_filho", "sku_pai"]` e `sku_filho: str | None`, com validação de que `sku_filho` é obrigatório quando a granularidade é `sku_filho`. Toda regra que exige SKU filho declara a dependência e retorna `NAO_AVALIAVEL` quando o registro é de SKU pai.

**Alternativa rejeitada:** rejeitar registros de SKU pai na leitura. Tornaria o esqueleto incapaz de rodar contra qualquer fonte agregada, e o problema é de origem, não de código.

### D2. Guardrails retornam três estados, não um booleano

`ResultadoGuardrail` é `APROVADO | BLOQUEADO | NAO_AVALIAVEL`, acompanhado de `guardrail: str` e `motivo: str`. Um booleano colapsaria "não sei" em "pode" — o modo de falha que os guardrails existem para impedir. A consolidação Top 3 considera apenas `APROVADO`.

**Alternativa rejeitada:** `bool | None`. Perde o motivo auditável e permite que `if not resultado` trate `None` como bloqueio ou aprovação, a depender do autor.

### D3. Zero é ausência apenas onde a semântica diz que é

Na fixture atual, nenhuma coluna de medição vem zerada em 100% das linhas. As colunas monetárias (`margem`, `receita_faturada`, `unidades_vendidas`, `valor_de_comissao`) têm 140 linhas em zero, e ali zero é "dia sem venda" — preservado. A conversão de zero em `None` fica como tabela explícita por coluna no mapeamento, populada apenas quando a view real exigir; a fixture não a aciona.

**Alternativa rejeitada:** tratar todo `0` como `None`. Destruiria a informação de "seller sem venda" e quebraria o cálculo de rentabilidade sobre GMV.

### D4. O mapeamento cobre dois vocabulários

`schema_mapping.py` declara a tabela `coluna_da_origem → campo_do_domínio` com uma coluna `origem` (`view` ou `fixture`) por entrada. O adapter mock resolve as entradas de `origem=fixture`; o adapter BigQuery resolverá `origem=view`. Campos sem entrada permanecem `None` e o guardrail que os exige retorna `NAO_AVALIAVEL`. Derivações declaradas (ex.: `winner_avg_price ← menor_preco_por_sku_dia` na view) são funções nomeadas na mesma tabela, não lógica espalhada.

**Alternativa rejeitada:** um único nome de coluna por campo. Faria o adapter mock e o adapter BigQuery divergirem silenciosamente na primeira mudança de view.

### D5. Normalização numérica com tolerância explícita

Resíduo de ponto flutuante (`abs(v) < 1e-9 → 0.0`) é aplicado a toda coluna numérica do mapeamento, com teste dedicado ao caso `1.1102230246251565e-16`. Texto vazio vira `None`. Valores monetários não recebem arredondamento no mapeamento — arredondamento é responsabilidade da apresentação.

### D6. Adapter BigQuery falha alto, não devolve vazio

`BigQuerySellerAdapter` é classe concreta que satisfaz `SellerDataPort` e levanta `NotImplementedError` com mensagem que nomeia a limitação. Retorno vazio seria indistinguível de "seller sem dados" e mascararia a falta de implementação na API. O `/health` reporta a dependência indisponível nesse caso.

### D7. `csv` da stdlib, não pandas

1.050 linhas de CSV simples. `csv.DictReader` com cache em memória no primeiro acesso resolve; `pandas` expandiria a árvore de dependências sem ganho. Reconsiderar apenas se o backend mock precisar de agregação pesada.

### D8. Fixtures ausentes não quebram a suíte

Como `tests/fixtures/*.csv` está no `.gitignore`, os testes **não podem** depender delas. Cada teste que precisa de dados escreve um CSV sintético em `tmp_path` e aponta o adapter para ele (o caminho das fixtures é configurável em `Settings`). O único teste que usa a fixture real é o de integração, e ele se auto-pula (`pytest.skip`) quando o arquivo não existe.

**Alternativa rejeitada:** commitar as fixtures com `git add -f`. Elas são dados internos e o `.gitignore` as exclui deliberadamente.

### D9. Grafo LangGraph sem LLM nesta change

`StateGraph` com estado `TypedDict`, roteamento por palavra-chave determinístico e nó de consolidação que aplica guardrails e Top 3. O nó de especialista é uma função substituta que devolve resposta fixa. Mantém o esqueleto executável e testável offline; a troca para Vertex AI fica restrita ao corpo desse nó.

**Alternativa rejeitada:** montar o grafo com `ChatVertexAI`. Exigiria ADC para rodar qualquer teste e travaria o CI.

### D10. Seleção de backend por factory explícita

`Settings` valida `DW_BACKEND ∈ {mock, bigquery}` e `MEMORY_BACKEND ∈ {memory}` na inicialização; valores fora disso derrubam o processo com mensagem que lista os aceitos. `build_seller_data_port(settings)` e `build_session_memory_port(settings)` resolvem as implementações. As rotas nunca instanciam adapter diretamente.

### D11. Erros de API sem vazamento

Handler global mapeia exceções de domínio para 4xx e qualquer exceção não tratada para 500, com `correlation_id` e mensagem genérica. Detalhe técnico vai só para o log.

### D12. Sintaxe compatível com 3.11, apesar de `target-version = "py313"`

`requires-python` declara `>=3.11,<3.14`. O ruff está configurado para `py313`, o que permitiria sintaxe que quebra em 3.11. O código se restringe ao que roda em 3.11; `target-version` fica como dívida de configuração para uma change de tooling.

## Risks / Trade-offs

- **[Funil monotônico na fixture]** → O gerador sintético foi corrigido para que `sessoes >= cliques >= carrinho >= envio >= pagamento >= faturadas` em 100% das linhas. Consequência: a fixture não exercita o caminho de queda real entre etapas; o diagnóstico de atrito só é testado com dados sintéticos controlados. Mitigação: `tests/unit/test_guardrails_funil.py` constrói registros com queda acentuada por etapa.
- **[`preco_de ≠ preco_por`]** → `receita_captada` não é `preco_de × unidades` (910 linhas divergem). Nenhuma regra desta change depende de `receita_captada`; o mapeamento a expõe como dado bruto, sem derivar preço dela.
- **[Fixtures no `.gitignore`]** → CI sem dados. Mitigação: D8 — testes sintéticos em `tmp_path`; integração auto-pulada.
- **[Divergência fixture × view]** → Nomes de coluna diferentes. Mitigação: D4 — tabela de mapeamento com coluna `origem`; o adapter BigQuery, quando implementado, só adiciona entradas.
- **[`ruff check .` falha hoje]** → 32 E501 em `scripts/generate_synthetic_data.py`, arquivo não versionado. Mitigação: a change inclui formatar esse script, ou excluí-lo da config do ruff se for artefato descartável. Decisão tomada na task de lint, não aqui.
- **[Sem autenticação real]** → `/chat` confia no `seller_id` da sessão. Mitigação: explícito como non-goal; o spec exige que o corpo da requisição nunca sobrescreva o valor da sessão.

## Migration Plan

Não há migração de dados. Deploy é a criação de módulos novos; nada existente é alterado além de `pyproject.toml` (só se necessário para lint) e `.env.example` (nenhuma variável nova obrigatória; acrescenta-se apenas o caminho das fixtures, com default).

Rollback: a change não altera comportamento em produção — não há produção. Reverter o merge da branch remove os módulos novos.

## Open Questions

Resolvidas para esta change (não bloqueiam as tasks):

- **Caminho das fixtures.** Decidido: configurável por `Settings` (`MOCK_DATA_PATH`, default `tests/fixtures/seller_sku_sales.csv`), e o construtor do adapter aceita override explícito. D8 depende disso; sem ele os testes não conseguiriam apontar para `tmp_path`.
- **Funil.** Resolvido: `scripts/generate_synthetic_data.py` foi corrigido (`random.uniform(1.08, 1.22)` → `random.uniform(0.65, 0.85)`) e as fixtures foram regeradas; o funil agora é monotônico em 100% das linhas. Nenhuma regra precisa contornar inversão.
- **`buybox_win_rate` na view real.** Não bloqueia: o adapter BigQuery é stub. Quando for implementado, o mapeamento decide entre ler a coluna direta ou derivar dos insumos.
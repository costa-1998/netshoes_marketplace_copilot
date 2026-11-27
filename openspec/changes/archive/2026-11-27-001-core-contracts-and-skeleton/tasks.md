# Tasks

## 1. Fundação do pacote e configuração

- [x] 1.1 Criar `src/kam_agent/adapters/__init__.py` e `src/kam_agent/config.py` com `Settings` (pydantic-settings) espelhando `.env.example`, incluindo `MOCK_DATA_PATH` (default `tests/fixtures/seller_sku_sales.csv`) e `MOCK_SELLER_MASTER_PATH`; verificar com `PYTHONPATH=src .venv/bin/python -c "from kam_agent.config import Settings; print(Settings())"` usando as variáveis do `.env.example`.
- [x] 1.2 Validar que `DW_BACKEND` aceita apenas `mock|bigquery` e `MEMORY_BACKEND` apenas `memory`, falhando na inicialização com mensagem que lista os valores aceitos; verificar com `tests/unit/test_config.py` cobrindo valor válido, inválido e ausente.
- [x] 1.3 Adicionar `MOCK_DATA_PATH` e `MOCK_SELLER_MASTER_PATH` ao `.env.example` com comentário; verificar que `Settings()` carrega os defaults sem essas variáveis definidas.
- [x] 1.4 Resolver os 32 erros E501 de `scripts/generate_synthetic_data.py` (formatar ou excluir da config do ruff, conforme decisão registrada no commit); verificar que `ruff check .` termina sem erros.

## 2. Contratos de domínio

- [x] 2.1 Implementar `src/kam_agent/domain/enums.py` com `Granularidade` (`sku_filho|sku_pai`), `ResultadoGuardrail` (`APROVADO|BLOQUEADO|NAO_AVALIAVEL`), `TipoGargalo`, `TipoRecomendacao` e `EtapaFunil`; verificar com `tests/unit/test_domain_enums.py` que importa todos e valida os membros exatos.
- [x] 2.2 Implementar `src/kam_agent/domain/models.py` com `PerformanceSKU` (granularidade, `sku_pai`, `sku_filho: str | None`, métricas `float | None`), `Recomendacao` (impacto financeiro estimado, tipo, justificativa, guardrails aplicáveis) e `ResultadoGuardrailDetalhado` (guardrail, resultado, motivo); verificar com `tests/unit/test_domain_models.py` que rejeita `granularidade="sku_filho"` sem `sku_filho` preenchido e aceita `sku_pai` sem ele.
- [x] 2.3 Implementar `src/kam_agent/domain/exceptions.py` com `DomainError`, `SellerNaoEncontrado`, `GranularidadeInsuficiente` e `SimulacaoInvalida`; verificar com `tests/unit/test_domain_exceptions.py` que todas herdam de `DomainError` e carregam mensagem legível.
- [x] 2.4 Confirmar que o pacote `domain` não importa `fastapi`, `langgraph`, `google.cloud` nem `pydantic_settings`; verificar com `tests/unit/test_domain_isolation.py` que inspeciona `sys.modules` após importar `kam_agent.domain` em subprocesso limpo.

## 3. Regras de guardrail

- [x] 3.1 Implementar em `src/kam_agent/domain/guardrails.py` o resultado de guardrail e a regra de granularidade (SKU pai → `NAO_AVALIAVEL`); verificar com `tests/unit/test_guardrails_granularidade.py` cobrindo registro `sku_filho` e registro `sku_pai`.
- [x] 3.2 Implementar a trava 1P; verificar com `tests/unit/test_guardrails_1p.py` cobrindo 1P ativo com preço acima do concorrente (bloqueia redução e campanha), 1P ativo com gargalo logístico (não bloqueia logística), 1P inativo (não bloqueia) e 1P desconhecido (→ `NAO_AVALIAVEL`).
- [x] 3.3 Implementar a priorização preço-vs-logística; verificar com `tests/unit/test_guardrails_buybox.py` cobrindo `delta_preco <= 0` com win rate < 50% e `delta_prazo > 0` (→ gargalo logístico), `delta_preco > 0` com margem (→ preço permitido) e win rate ausente (→ `NAO_AVALIAVEL`).
- [x] 3.4 Implementar a regra de ruptura em Curva A; verificar com `tests/unit/test_guardrails_curva_a.py` cobrindo Curva A com cobertura ≤ 3 dias (→ bloqueia redução de preço e prioriza reposição), Curva A com cobertura > 3 dias e curva ausente (→ `NAO_AVALIAVEL`).
- [x] 3.5 Implementar o diagnóstico de funil e cancelamento; verificar com `tests/unit/test_guardrails_funil.py` cobrindo queda acentuada entre etapas consecutivas (com registro sintético, já que a fixture é monotônica), taxa `cancelamentos / compras_faturadas > 0.15` e etapa ausente (→ `NAO_AVALIAVEL`).
- [x] 3.6 Implementar o piso de rentabilidade em `src/kam_agent/domain/price_simulation.py`, recalculando a rentabilidade projetada ao reduzir `preco_por` para `winner_avg_price` com o `percentual_de_comissao` vigente; verificar com `tests/unit/test_price_simulation.py` cobrindo rentabilidade projetada acima de 5% (aceita), em 5% ou menos (rejeitada) e comissão/margem ausente (→ `NAO_AVALIAVEL`).
- [x] 3.7 Implementar a consolidação Top 3 com desempate determinístico; verificar com `tests/unit/test_guardrails_top3.py` cobrindo mais de três candidatas, empate na fronteira do corte (resultado estável entre execuções), zero candidatas elegíveis e que `BLOQUEADO`/`NAO_AVALIAVEL` nunca ocupam vaga.

## 4. Portas

- [x] 4.1 Implementar `src/kam_agent/ports/seller_data.py` com o `Protocol` `SellerDataPort` (`@runtime_checkable`) expondo leitura por `seller_id` + `data_inicio`/`data_fim` e um DTO de resultado; verificar com `tests/unit/test_ports_seller_data.py` que um stub que satisfaz o protocolo é aceito por `isinstance` e que um objeto sem o método não é.
- [x] 4.2 Implementar `src/kam_agent/ports/session_memory.py` com o `Protocol` `SessionMemoryPort` (ler, gravar, apagar) marcado `@runtime_checkable`; verificar com `tests/unit/test_ports_session_memory.py` que o protocolo cobre os três métodos e que um stub o satisfaz.

## 5. Mapeamento de schema e adapter mock

- [x] 5.1 Implementar `src/kam_agent/adapters/schema_mapping.py` como tabela explícita `(coluna, campo_do_dominio, origem, derivacao)` cobrindo os dois vocabulários — nomes da fixture (`preco_por`, `delta_preco`, `tem_1p`, `winner_avg_price`) e da view (`preco_por_fim_dia`, `gap_preco_vs_menor_sku_pct`, `flag_1p_ativo_sku`, `menor_preco_por_sku_dia`) — com a tabela de semântica de zero por coluna; verificar com `tests/unit/test_schema_mapping.py` que cada campo sem origem declarada permanece `None` e que toda entrada tem `origem` válida.
- [x] 5.2 Implementar a normalização de valores em `schema_mapping.py`: ruído de ponto flutuante (`abs(v) < 1e-9 → 0.0`), texto vazio como `None` e zero→`None` apenas nas colunas declaradas na tabela de semântica; verificar com `tests/unit/test_schema_normalization.py` incluindo o caso `1.1102230246251565e-16` e confirmando que `unidades_vendidas == 0` é preservado.
- [x] 5.3 Implementar `src/kam_agent/adapters/mock_seller_data.py` lendo o CSV configurado em `Settings` com `csv.DictReader` (ou caminho injetado no construtor), cacheando em memória, filtrando por `seller_id` e janela inclusiva e marcando `granularidade="sku_filho"` quando `sku_filho` estiver presente; verificar com `tests/unit/test_mock_adapter.py` usando CSV sintético em `tmp_path` que o filtro por seller e por data retorna exatamente as linhas esperadas e que um seller inexistente devolve coleção vazia.
- [x] 5.4 Implementar a rejeição de leitura sem `seller_id` e de janela com data inicial > final na porta e no adapter mock; verificar com `tests/unit/test_mock_adapter_errors.py` que nenhuma leitura de arquivo ocorre nesses casos (arquivo inexistente no caminho não gera `FileNotFoundError`).
- [x] 5.5 Implementar a guarda de contaminação: registro com `seller_id` diferente do solicitado é descartado e a inconsistência é registrada; verificar com `tests/unit/test_mock_adapter_isolation.py` usando CSV sintético com linha de outro seller e assertando que a linha não aparece no resultado e que a inconsistência foi logada.
- [x] 5.6 Adicionar ao `docs/reference/dicionario_de_dados_copiloto_seller_sku_diario.md` a seção de mapeamento view → domínio e as lacunas conhecidas (vocabulário divergente entre fixture e view, `preco_de ≠ preco_por`, `receita_captada` não derivável de `preco_de × unidades`, colunas da view ausentes na fixture); verificar que a seção existe, cita `schema_mapping.py` e lista cada lacuna acima.

## 6. Adapter BigQuery, memória de sessão e factory

- [x] 6.1 Implementar `src/kam_agent/adapters/bigquery_seller_data.py` como classe concreta que satisfaz `SellerDataPort` e levanta `NotImplementedError` com mensagem nomeando a limitação; verificar com `tests/unit/test_bigquery_adapter.py` que a chamada levanta o erro, que a mensagem não está vazia e que `isinstance(adapter, SellerDataPort)` é verdadeiro.
- [x] 6.2 Implementar `src/kam_agent/adapters/in_memory_session.py` com isolamento por chave de sessão e TTL desde a última escrita, usando relógio injetável; verificar com `tests/unit/test_in_memory_session.py` cobrindo leitura da própria sessão, sessão inexistente, leitura cruzada, expiração, renovação por nova escrita e remoção idempotente.
- [x] 6.3 Implementar a factory `build_seller_data_port(settings)` e `build_session_memory_port(settings)` em `src/kam_agent/adapters/factory.py`; verificar com `tests/unit/test_factory.py` que `mock` devolve o adapter mock, `bigquery` devolve o adapter BigQuery, `memory` devolve o adapter em memória e um valor desconhecido falha na construção.

## 7. Ferramentas determinísticas

- [x] 7.1 Implementar `src/kam_agent/tools/seller_performance.py` expondo uma ferramenta que recebe `seller_id` injetado pelo estado (não como parâmetro do chamador) e devolve o resumo de performance; verificar com `tests/unit/test_tool_seller_performance.py` que a assinatura pública não expõe `seller_id` como argumento de entrada e que a ferramenta usa o seller do estado.
- [x] 7.2 Implementar `src/kam_agent/tools/gargalo.py` que classifica o gargalo a partir de um `PerformanceSKU`, delegando às regras de guardrail; verificar com `tests/unit/test_tool_gargalo.py` que registro de granularidade `sku_pai` resulta em `NAO_AVALIAVEL` nas regras que exigem SKU filho.

## 8. Grafo de orquestração

- [x] 8.1 Implementar `src/kam_agent/agents/state.py` com o `TypedDict` de estado (`seller_id`, `mensagem`, `especialista`, `recomendacoes`, `guardrails`, `resposta`, `erro`, `correlation_id`); verificar com `tests/unit/test_agent_state.py` que o estado mínimo é construível e que `seller_id` é obrigatório.
- [x] 8.2 Implementar `src/kam_agent/agents/router.py` com roteamento determinístico por intenção e caminho explícito para intenção não reconhecida; verificar com `tests/unit/test_router.py` cobrindo intenção suportada, intenção não suportada (→ resposta padrão, sem erro) e determinismo (mesma entrada, mesma saída).
- [x] 8.3 Implementar `src/kam_agent/agents/graph.py` montando o `StateGraph` com nós de roteamento, especialista substituto (sem LLM) e consolidação; verificar com `tests/unit/test_graph.py` que uma execução completa devolve resposta e estado final sem chamada de rede (assertando que nenhum cliente HTTP é instanciado).
- [x] 8.4 Implementar a interrupção do fluxo quando `seller_id` está ausente e o registro de falha no estado quando uma etapa levanta erro; verificar com `tests/unit/test_graph_errors.py` que a execução sem seller não consulta dados e que o erro de etapa popula `erro` e `correlation_id` sem propagar a exceção bruta.
- [x] 8.5 Garantir que a consolidação remove recomendações bloqueadas e aplica Top 3 antes de devolver; verificar com `tests/unit/test_graph_consolidation.py` usando especialista substituto que propõe recomendação bloqueada e mais de três candidatas.

## 9. API FastAPI

- [x] 9.1 Implementar `src/kam_agent/api/schemas.py` com os modelos de requisição e resposta do chat; verificar com `tests/unit/test_api_schemas.py` que mensagem vazia é rejeitada e que um `seller_id` presente no corpo não é propagado para o comando construído.
- [x] 9.2 Implementar `src/kam_agent/api/dependencies.py` resolvendo portas via factory a partir de `Settings`; verificar com `tests/unit/test_api_dependencies.py` que a dependência devolve as implementações corretas por backend.
- [x] 9.3 Implementar `src/kam_agent/api/routes.py` com `GET /health` e `POST /chat`, derivando `seller_id` da sessão e criando sessão quando ausente; verificar com `tests/unit/test_api_routes.py` usando `TestClient` cobrindo mensagem válida, mensagem vazia (422), sessão ausente (cria) e `seller_id` divergente no corpo (ignorado).
- [x] 9.4 Implementar o handler global de erros mapeando exceções de domínio para 4xx e falhas inesperadas para 500 com `correlation_id`; verificar com `tests/unit/test_api_errors.py` que o corpo de erro não contém stack trace, nome de tabela, caminho de arquivo nem credencial.
- [x] 9.5 Implementar `src/kam_agent/api/app.py` com `create_app()` que falha na inicialização quando a configuração é inválida; verificar com `tests/unit/test_api_app.py` que configuração inválida levanta erro na criação e válida responde 200 em `/health` com os backends em uso.
- [x] 9.6 Confirmar que `/health` reporta indisponibilidade nomeando a dependência quando o adapter BigQuery está selecionado e não implementado; verificar com `tests/unit/test_api_health.py`.
- [x] 9.7 Atualizar `README.md` com instruções de execução offline (`DW_BACKEND=mock`), como subir a API e como rodar os testes; verificar executando literalmente os comandos documentados.

## 10. Integração e fechamento

- [x] 10.1 Escrever `tests/integration/test_end_to_end_chat.py` executando `POST /chat` com `DW_BACKEND=mock` e seller `10024`, verificando que a resposta retorna, respeita Top 3 e não contém recomendação bloqueada por 1P; verificar que o teste se auto-pula quando `tests/fixtures/seller_sku_sales.csv` está ausente (caso do CI) e passa localmente.
- [x] 10.2 Rodar `ruff check .`, `ruff format --check .` e `pytest` completos e corrigir todas as falhas; verificar que a suíte termina com zero falhas e zero erros de lint.
# Dicionário de Dados e Funcionamento da Query — `pdia0024.curated_netshoes.copiloto_seller_sku_diario`

## 1. Respostas que Alterariam a Regra `flag_1p_ativo_sku`

Na query atual, `flag_1p_ativo_sku` assume `TRUE` quando existe estoque `1P` ativo no mesmo `data` e `sku_pai` (bloqueando alertas de reposição ou ajuste de preço para o seller `3P` naquele item). Você deveria alterar essa lógica caso o time de Buy Box (Bruno Eyng / Champs) ou o time comercial (Letícia) respondam o seguinte:

1. **Disputa por SKU filho em vez de SKU pai:** Se o 1P tiver estoque apenas em alguns tamanhos/variações (SKU filho) e o seller `3P` vender um tamanho sem estoque 1P, bloquear o `sku_pai` inteiro pode esconder oportunidades reais.
2. **Threshold mínimo de estoque ou cobertura do 1P:** Se um estoque residual muito baixo do 1P não for suficiente para sustentar a Buy Box (ou se o 1P tiver prazo de entrega pior que o 3P em determinadas regiões), exigir apenas `qtd_estoque_total > 0` pode ser restritivo demais.
3. **Exceções de sortimento / campanhas:** Se a operação comercial autorizar orientar sellers `3P` mesmo com presença `1P` em cenários específicos (ex.: campanhas sazonais ou categorias em que o `3P` tem condição superior), a trava deixa de ser um bloqueio absoluto e vira um peso/penalidade no score.

---

## 2. Como a Query Funciona

A query transforma a base horária e volumosa `magalu-bigdata-netshoes.hora_hora.tbl_hh_base_hora_hora` em uma tabela diária analítica (`pdia0024.curated_netshoes.copiloto_seller_sku_diario`) voltada para o motor do copiloto:

1. **Particionamento e clusterização:** A tabela final é particionada por `data` (`DAY`) e clusterizada por `seller_id, sku_pai`, reduzindo custo e tempo de leitura nas consultas por janela de tempo e por loja.
2. **Recorte temporal e de negócio (`base_filtrada`):** Restringe a janela aos últimos 30 dias (`WHERE data >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)`) e filtra o escopo da Netshoes (`unidade_de_negocio_detalhada = 'NETSHOES'`).
3. **Snapshot final do dia (`snapshot_dia_sku`):** Identifica o último registro do dia por `(data, seller_id, sku_pai, source)` ordenando por `dt_att DESC, hora DESC`, permitindo capturar o estado de fechamento do dia para estoque, preço e prazo.
4. **Agregação diária (`agregado_diario`):** Consolida métricas acumuladas no dia (`SUM` de sessões, pedidos, GMV, valores captados, receita, margem e custos) e mantém o último estado do dia (`MAX` com `rn_ultimo_snap = 1` para estoque, cobertura, ruptura, giro, preço e prazo).
5. **Cobertura 1P e referência de competitividade (`cobertura_1p_dia` e `referencia_sku_dia`):**
   - `cobertura_1p_dia` verifica se houve estoque `1P` ativo no mesmo `data` e `sku_pai`.
   - `referencia_sku_dia` calcula o menor `preco_por` e o menor `prazo_visto_pond` observados no mesmo `data` e `sku_pai` para servir de referência comparativa.
6. **Saída filtrada para 3P:** Cruza os dados diários do seller `3P` com a flag do `1P` e com as referências de preço/prazo, mantendo apenas `source = '3P'` (sem expor números absolutos de terceiros).

---

## 3. Dicionário de Colunas da Tabela Final

### Identificação e Contexto da Loja/Produto
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `data` | `DATE` | Data de referência do registro diário (chave de particionamento). |
| `seller_id` | `STRING` | Identificador único do seller na plataforma (chave de clusterização e cruzamento). |
| `seller_name` | `STRING` | Nome da loja/seller. |
| `carteira` | `STRING` | Carteira à qual o seller pertence na estrutura da Netshoes. |
| `classificacao` | `STRING` | Classificação do seller/operação na base. |
| `source` | `STRING` | Origem da operação na tabela final (`'3P'`). |
| `sku_pai` | `STRING` | Identificador do produto pai/modelo. |
| `desc_produto` | `STRING` | Descrição/nome do produto. |
| `categoria_de_produto` | `STRING` | Categoria do produto no catálogo. |
| `departamento` | `STRING` | Departamento ao qual o produto pertence. |
| `marca` | `STRING` | Marca do produto. |
| `desc_sazonalidade` | `STRING` | Indicação de sazonalidade/campanha associada ao item. |

### Trava 1P, Estoque e Ruptura
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `flag_1p_ativo_sku` | `BOOL` | Indica se houve estoque próprio (`1P`) ativo no mesmo `data` e `sku_pai` (trava de proteção da Buy Box 1P). |
| `flag_estoque_fim_dia` | `STRING` | Indicador de disponibilidade de estoque no último snapshot do dia. |
| `qtd_estoque_total_fim_dia` | `INT64` | Quantidade total de estoque registrada no fechamento do dia. |
| `faixa_de_cobertura_fim_dia` | `STRING` | Faixa de cobertura de estoque no fechamento do dia. |
| `ruptura_fim_dia` | `FLOAT64` | Indicador/percentual de ruptura registrado no fechamento do dia. |
| `vmd_com_estoque_fim_dia` | `FLOAT64` | Venda média diária com estoque no fechamento do dia (termômetro de giro). |

### Competitividade (Preço e Prazo)
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `preco_por_fim_dia` | `FLOAT64` | Preço "por" praticado pelo seller no fechamento do dia. |
| `preco_netshoes_fim_dia` | `NUMERIC` | Preço de referência da Netshoes no fechamento do dia. |
| `preco_mercado_fim_dia` | `NUMERIC` | Preço de referência de mercado no fechamento do dia. |
| `menor_preco_por_sku_dia` | `FLOAT64` | Menor `preco_por` observado no mesmo `data` e `sku_pai` entre os registros avaliados. |
| `gap_preco_vs_menor_sku_pct` | `FLOAT64` | Diferença percentual entre `preco_por_fim_dia` e `menor_preco_por_sku_dia` (`(preco_seller - menor_preco) / menor_preco`). |
| `prazo_visto_pond_fim_dia` | `INT64` | Prazo ponderado exibido/visto no fechamento do dia. |
| `prazo_prometido_fim_dia` | `FLOAT64` | Prazo prometido de entrega no fechamento do dia. |
| `menor_prazo_visto_sku_dia` | `INT64` | Menor `prazo_visto_pond` observado no mesmo `data` e `sku_pai`. |
| `diff_prazo_vs_menor_sku` | `INT64` | Diferença absoluta em dias/unidades de prazo entre o seller e o menor prazo do `sku_pai`. |

### Tráfego, Conversão e Volume
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `sessao_pdp_dia` | `INT64` | Soma de sessões na página de produto (PDP) no dia. |
| `pedido_pdp_dia` | `INT64` | Soma de pedidos originados na PDP no dia. |
| `taxa_conversao_pdp_dia` | `FLOAT64` | Relação `pedido_pdp_dia / sessao_pdp_dia` no dia. |
| `gmv_dia` | `FLOAT64` | Soma do GMV no dia. |
| `vlr_captado_dia` | `NUMERIC` | Soma do valor captado bruto no dia. |
| `vlr_captado_liquido_dia` | `NUMERIC` | Soma do valor captado líquido no dia. |

### Rentabilidade e Custos (*Cash Margin*)
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `vlr_receita_liquida_nova_dia` | `FLOAT64` | Soma da receita líquida (`_nova`) no dia. |
| `vlr_margem_bruta_nova_dia` | `FLOAT64` | Soma da margem bruta (`_nova`) no dia. |
| `vlr_comissao_fat_dia` | `NUMERIC` | Soma do valor de comissão faturada no dia. |
| `vlr_custo_frete_dia` | `FLOAT64` | Soma do custo de frete no dia. |
| `mdr_total_dia` | `NUMERIC` | Soma do custo de MDR no dia. |
| `vlr_devolucao_dia` | `FLOAT64` | Soma do valor de devoluções no dia. |
| `margem_bruta_sobre_gmv_dia` | `FLOAT64` | Razão `vlr_margem_bruta_nova_dia / gmv_dia` no dia (insumo auxiliar até confirmação da fórmula oficial de *cash margin* > 5%). |
---

## 4. Mapeamento View → Domínio e Lacunas Conhecidas

O ponto único de tradução entre as colunas desta view e os modelos Pydantic do domínio é
`src/kam_agent/adapters/schema_mapping.py` (tabela `MAPEAMENTO`). Cada entrada declara
`(campo_do_dominio, origem, coluna, derivacao)`; `origem` distingue `view` (esta tabela) de
`fixture` (os CSVs de `tests/fixtures/`).

### 4.1 Vocabulário divergente entre fixture e view

A fixture usa nomes próximos do domínio; a view usa nomes de origem. O mapeamento cobre os
dois vocabulários na mesma tabela:

| Campo do domínio | Coluna da fixture | Coluna da view |
| :--- | :--- | :--- |
| `id_seller` | `id_seller` | `seller_id` |
| `nome_produto` | `nome_produto` | `desc_produto` |
| `categoria_do_produto` | `categoria_do_produto` | `categoria_de_produto` |
| `preco_por` | `preco_por` | `preco_por_fim_dia` |
| `delta_preco` | `delta_preco` | `gap_preco_vs_menor_sku_pct` |
| `delta_prazo` | `delta_prazo` | `diff_prazo_vs_menor_sku` |
| `tem_1p` | `tem_1p` | `flag_1p_ativo_sku` |
| `winner_avg_price` | `winner_avg_price` | derivado de `menor_preco_por_sku_dia` |
| `winner_avg_prazo` | `winner_avg_prazo` | `menor_prazo_visto_sku_dia` |
| `cobertura` | `cobertura` | `faixa_de_cobertura_fim_dia` |
| `vmd` | `vmd` | `vmd_com_estoque_fim_dia` |
| `receita_captada` | `receita_captada` | `vlr_captado_dia` |
| `receita_faturada` | `receita_faturada` | `vlr_receita_liquida_nova_dia` |
| `margem` | `margem` | `vlr_margem_bruta_nova_dia` |
| `valor_de_comissao` | `valor_de_comissao` | `vlr_comissao_fat_dia` |
| `custo_frete` | `custo_frete` | `vlr_custo_frete_dia` |
| `sessoes` | `sessoes` | `sessao_pdp_dia` |
| `compras_faturadas` | `compras_faturadas` | `pedido_pdp_dia` |
| `taxa_conversao` | `taxa_conversao` | `taxa_conversao_pdp_dia` |

### 4.2 Colunas da view ausentes na fixture

`seller_name`, `carteira`, `classificacao`, `source`, `departamento`, `marca`,
`desc_sazonalidade`, `preco_netshoes_fim_dia`, `preco_mercado_fim_dia`,
`prazo_prometido_fim_dia`, `vlr_captado_liquido_dia`, `gmv_dia`, `mdr_total_dia`,
`vlr_devolucao_dia`, `margem_bruta_sobre_gmv_dia`. Nenhuma delas é exigida por guardrail
nesta change; ficam como campos sem origem declarada e permanecem `None`.

### 4.3 Lacunas e inconsistências conhecidas

- **`preco_de ≠ preco_por` em 100% das linhas da fixture.** O preço "de" é promocional, e
  `receita_captada` **não** é derivável como `preco_de × unidades_vendidas` (910 linhas
  divergem). Nenhuma regra desta change deriva preço de `receita_captada`; o campo é
  exposto como dado bruto.
- **`sessoes` vs `cliques`.** A fixture original trazia `sessoes < cliques` em todas as
  linhas; o gerador foi corrigido e a fixture foi regerada monotônica. Ainda assim, a regra
  de funil **não** usa `sessoes` na comparação: opera sobre
  `cliques → carrinho → envio → pagamento → faturadas`, como a constituição exige.
- **`categoria_curva` sem equivalente na view.** A view não expõe `curva_abc`; o guardrail de
  ruptura em Curva A é permanentemente `NAO_AVALIAVEL` no backend BigQuery até a view ganhar
  essa coluna.
- **`buybox_win_rate` sem coluna direta na view.** A view expõe os insumos
  (`gap_preco_vs_menor_sku_pct`, `diff_prazo_vs_menor_sku`); a derivação da taxa de vitória
  será decidida quando o adapter BigQuery for implementado.
- **Grão.** A view é clusterizada por `seller_id, sku_pai`; a fixture já traz `sku_filho`. Se
  a view não expuser SKU filho, todo registro virá com `granularidade="sku_pai"` e os
  guardrails que exigem SKU filho resultarão em `NAO_AVALIAVEL` — comportamento honesto, não
  erro de código.
- **Zero com semântica de ausência.** `vmd`, `cobertura`, `sessoes` e `compras_faturadas` na
  view são marcados com `zero_e_ausencia=True` no mapeamento: `0` vira `None`. Colunas
  monetárias preservam `0` como "dia sem venda".

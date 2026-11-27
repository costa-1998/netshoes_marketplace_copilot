"""Mapeamento explícito entre colunas da origem e campos do domínio (D4/D5).

O adapter mock lê a fixture; o adapter BigQuery lerá a view
``copiloto_seller_sku_diario``. Os dois vocabulários convivem nesta tabela,
cada entrada declarando sua ``origem``. Campo sem entrada permanece ``None``
e o guardrail que o exige degrada para ``NAO_AVALIAVEL``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

Origem = Literal["fixture", "view"]

#: Tolerância para resíduo de ponto flutuante.
TOLERANCIA_NUMERICA = 1e-9


@dataclass(frozen=True, slots=True)
class EntradaMapeamento:
    """Uma coluna de origem traduzida para um campo do domínio."""

    campo: str
    origem: Origem
    coluna: str | None = None
    derivacao: Callable[[Mapping[str, Any]], Any] | None = None
    zero_e_ausencia: bool = False
    numerico: bool = True


def _texto(valor: Any) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def _float(valor: Any) -> float | None:
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        if not valor:
            return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if abs(numero) < TOLERANCIA_NUMERICA:
        return 0.0
    return numero


def _booleano(valor: Any) -> bool | None:
    if valor is None:
        return None
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().lower()
    if not texto:
        return None
    if texto in {"true", "1", "sim", "yes"}:
        return True
    if texto in {"false", "0", "nao", "não", "no"}:
        return False
    return None


def _menor_preco_do_sku(colunas: Mapping[str, Any]) -> float | None:
    """Derivação declarada para ``winner_avg_price`` a partir da view."""
    return _float(colunas.get("menor_preco_por_sku_dia"))


#: Tabela canônica coluna → campo do domínio.
MAPEAMENTO: tuple[EntradaMapeamento, ...] = (
    # Identificação — mesmo nome nos dois vocabulários.
    EntradaMapeamento("data", "fixture", "data", numerico=False),
    EntradaMapeamento("data", "view", "data", numerico=False),
    EntradaMapeamento("id_seller", "fixture", "id_seller", numerico=False),
    EntradaMapeamento("id_seller", "view", "seller_id", numerico=False),
    EntradaMapeamento("sku_pai", "fixture", "sku_pai", numerico=False),
    EntradaMapeamento("sku_pai", "view", "sku_pai", numerico=False),
    EntradaMapeamento("sku_filho", "fixture", "sku_filho", numerico=False),
    EntradaMapeamento("sku_filho", "view", "sku_filho", numerico=False),
    EntradaMapeamento("nome_produto", "fixture", "nome_produto", numerico=False),
    EntradaMapeamento("nome_produto", "view", "desc_produto", numerico=False),
    EntradaMapeamento("categoria_do_produto", "fixture", "categoria_do_produto", numerico=False),
    EntradaMapeamento("categoria_do_produto", "view", "categoria_de_produto", numerico=False),
    EntradaMapeamento("categoria_curva", "fixture", "categoria_curva", numerico=False),
    # Curva ABC não existe na view: permanece ausente.
    # Estoque e giro.
    EntradaMapeamento("vmd", "fixture", "vmd"),
    EntradaMapeamento("vmd", "view", "vmd_com_estoque_fim_dia", zero_e_ausencia=True),
    EntradaMapeamento("estoque", "fixture", "estoque"),
    EntradaMapeamento("estoque", "view", "qtd_estoque_total_fim_dia"),
    EntradaMapeamento("cobertura", "fixture", "cobertura"),
    EntradaMapeamento("cobertura", "view", "faixa_de_cobertura_fim_dia", zero_e_ausencia=True),
    # Receita e margem.
    EntradaMapeamento("unidades_vendidas", "fixture", "unidades_vendidas"),
    EntradaMapeamento("receita_captada", "fixture", "receita_captada"),
    EntradaMapeamento("receita_captada", "view", "vlr_captado_dia"),
    EntradaMapeamento("receita_faturada", "fixture", "receita_faturada"),
    EntradaMapeamento("receita_faturada", "view", "vlr_receita_liquida_nova_dia"),
    EntradaMapeamento("percentual_de_comissao", "fixture", "percentual_de_comissao"),
    EntradaMapeamento("valor_de_comissao", "fixture", "valor_de_comissao"),
    EntradaMapeamento("valor_de_comissao", "view", "vlr_comissao_fat_dia"),
    EntradaMapeamento("margem", "fixture", "margem"),
    EntradaMapeamento("margem", "view", "vlr_margem_bruta_nova_dia"),
    EntradaMapeamento("rentabilidade", "fixture", "rentabilidade"),
    # Preço e competitividade.
    EntradaMapeamento("preco_de", "fixture", "preco_de"),
    EntradaMapeamento("preco_por", "fixture", "preco_por"),
    EntradaMapeamento("preco_por", "view", "preco_por_fim_dia"),
    EntradaMapeamento("preco_1p", "fixture", "preco_1p"),
    EntradaMapeamento("delta_preco", "fixture", "delta_preco"),
    EntradaMapeamento("delta_preco", "view", "gap_preco_vs_menor_sku_pct"),
    EntradaMapeamento("prazo_medio_envio", "fixture", "prazo_medio_envio"),
    EntradaMapeamento("prazo_medio_envio", "view", "prazo_visto_pond_fim_dia"),
    EntradaMapeamento("delta_prazo", "fixture", "delta_prazo"),
    EntradaMapeamento("delta_prazo", "view", "diff_prazo_vs_menor_sku"),
    EntradaMapeamento("custo_frete", "fixture", "custo_frete"),
    EntradaMapeamento("custo_frete", "view", "vlr_custo_frete_dia"),
    EntradaMapeamento("tem_1p", "fixture", "tem_1p", numerico=False),
    EntradaMapeamento("tem_1p", "view", "flag_1p_ativo_sku", numerico=False),
    EntradaMapeamento("buybox_win_rate", "fixture", "buybox_win_rate"),
    EntradaMapeamento("winner_avg_price", "fixture", "winner_avg_price"),
    EntradaMapeamento("winner_avg_price", "view", None, derivacao=_menor_preco_do_sku),
    EntradaMapeamento("winner_avg_prazo", "fixture", "winner_avg_prazo"),
    EntradaMapeamento("winner_avg_prazo", "view", "menor_prazo_visto_sku_dia"),
    # Funil.
    EntradaMapeamento("sessoes", "fixture", "sessoes"),
    EntradaMapeamento("sessoes", "view", "sessao_pdp_dia", zero_e_ausencia=True),
    EntradaMapeamento("cliques", "fixture", "cliques"),
    EntradaMapeamento("adicao_ao_carrinho", "fixture", "adicao_ao_carrinho"),
    EntradaMapeamento(
        "adicao_de_informacoes_de_envio", "fixture", "adicao_de_informacoes_de_envio"
    ),
    EntradaMapeamento("adicao_de_pagamento", "fixture", "adicao_de_pagamento"),
    EntradaMapeamento("compras_faturadas", "fixture", "compras_faturadas"),
    EntradaMapeamento("compras_faturadas", "view", "pedido_pdp_dia", zero_e_ausencia=True),
    EntradaMapeamento("cancelamentos", "fixture", "cancelamentos"),
    EntradaMapeamento("taxa_conversao", "fixture", "taxa_conversao"),
    EntradaMapeamento("taxa_conversao", "view", "taxa_conversao_pdp_dia"),
)


def entradas_por_origem(origem: Origem) -> tuple[EntradaMapeamento, ...]:
    """Entradas declaradas para uma origem, na ordem da tabela."""
    return tuple(e for e in MAPEAMENTO if e.origem == origem)


def campos_sem_origem(origem: Origem) -> frozenset[str]:
    """Campos do domínio que nenhuma coluna da origem fornece."""
    from kam_agent.domain.models import PerformanceSKU

    fornecidos = {e.campo for e in entradas_por_origem(origem)}
    return frozenset(PerformanceSKU.model_fields) - fornecidos


def normalizar_numero(valor: Any) -> float | None:
    """Normaliza número: vazio → ``None``, resíduo < 1e-9 → ``0.0``."""
    return _float(valor)


def normalizar_texto(valor: Any) -> str | None:
    """Normaliza texto: vazio → ``None``."""
    return _texto(valor)


def normalizar_booleano(valor: Any) -> bool | None:
    """Normaliza booleano textual."""
    return _booleano(valor)


def converter_registro(colunas: Mapping[str, Any], origem: Origem) -> dict[str, Any]:
    """Traduz uma linha da origem em campos do domínio.

    Campos sem entrada declarada simplesmente não aparecem no resultado e
    permanecem ``None`` no modelo.
    """
    convertidos: dict[str, Any] = {}
    for entrada in entradas_por_origem(origem):
        if entrada.derivacao is not None:
            valor = entrada.derivacao(colunas)
        elif entrada.coluna is not None:
            valor = colunas.get(entrada.coluna)
        else:
            continue

        if entrada.numerico:
            normalizado: Any = _float(valor)
            if normalizado == 0.0 and entrada.zero_e_ausencia:
                normalizado = None
        elif entrada.campo == "tem_1p":
            normalizado = _booleano(valor)
        else:
            normalizado = _texto(valor)

        convertidos[entrada.campo] = normalizado
    return convertidos

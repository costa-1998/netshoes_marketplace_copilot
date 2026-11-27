"""Enums de domínio do copiloto KAM.

Sem dependência de GCP, FastAPI ou LangGraph (D1/D2 do design).
"""

from __future__ import annotations

from enum import StrEnum


class Granularidade(StrEnum):
    """Nível de agregação de um registro de performance."""

    SKU_FILHO = "sku_filho"
    SKU_PAI = "sku_pai"


class ResultadoGuardrail(StrEnum):
    """Estado de decisão de um guardrail — nunca um booleano (D2)."""

    APROVADO = "aprovado"
    BLOQUEADO = "bloqueado"
    NAO_AVALIAVEL = "nao_avaliavel"


class TipoGargalo(StrEnum):
    """Categoria de gargalo identificada em um SKU."""

    RUPTURA_CURVA_A = "ruptura_curva_a"
    LOGISTICA_PRAZO_FRETE = "logistica_prazo_frete"
    PRECO_ACIMA_CONCORRENTE = "preco_acima_concorrente"
    TRAVA_1P = "trava_1p"
    ATRITO_CHECKOUT = "atrito_checkout"
    CANCELAMENTO_ALTO = "cancelamento_alto"
    NENHUM = "nenhum"
    NAO_AVALIAVEL = "nao_avaliavel"


class TipoRecomendacao(StrEnum):
    """Ação recomendável ao seller."""

    REPOSICAO_ESTOQUE = "reposicao_estoque"
    REDUCAO_PRECO = "reducao_preco"
    AJUSTE_FRETE_PRAZO = "ajuste_frete_prazo"
    INVESTIGAR_CANCELAMENTO = "investigar_cancelamento"
    AJUSTE_FUNIL = "ajuste_funil"
    NENHUMA = "nenhuma"


class EtapaFunil(StrEnum):
    """Etapas do funil de conversão, em ordem."""

    SESSOES = "sessoes"
    CLIQUES = "cliques"
    CARRINHO = "adicao_ao_carrinho"
    ENVIO = "adicao_de_informacoes_de_envio"
    PAGAMENTO = "adicao_de_pagamento"
    FATURADAS = "compras_faturadas"

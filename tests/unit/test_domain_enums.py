"""Testes dos enums de domínio (task 2.1)."""

from __future__ import annotations

from kam_agent.domain.enums import (
    EtapaFunil,
    Granularidade,
    ResultadoGuardrail,
    TipoGargalo,
    TipoRecomendacao,
)


def test_granularidade_membros() -> None:
    assert {g.value for g in Granularidade} == {"sku_filho", "sku_pai"}


def test_resultado_guardrail_membros() -> None:
    assert {r.value for r in ResultadoGuardrail} == {
        "aprovado",
        "bloqueado",
        "nao_avaliavel",
    }


def test_tipo_gargalo_membros() -> None:
    assert TipoGargalo.RUPTURA_CURVA_A in TipoGargalo
    assert TipoGargalo.LOGISTICA_PRAZO_FRETE in TipoGargalo
    assert TipoGargalo.PRECO_ACIMA_CONCORRENTE in TipoGargalo
    assert TipoGargalo.TRAVA_1P in TipoGargalo
    assert TipoGargalo.ATRITO_CHECKOUT in TipoGargalo
    assert TipoGargalo.CANCELAMENTO_ALTO in TipoGargalo
    assert TipoGargalo.NAO_AVALIAVEL in TipoGargalo


def test_tipo_recomendacao_membros() -> None:
    assert TipoRecomendacao.REPOSICAO_ESTOQUE in TipoRecomendacao
    assert TipoRecomendacao.REDUCAO_PRECO in TipoRecomendacao
    assert TipoRecomendacao.AJUSTE_FRETE_PRAZO in TipoRecomendacao
    assert TipoRecomendacao.NENHUMA in TipoRecomendacao


def test_etapa_funil_ordem() -> None:
    valores = [e.value for e in EtapaFunil]
    assert valores == [
        "sessoes",
        "cliques",
        "adicao_ao_carrinho",
        "adicao_de_informacoes_de_envio",
        "adicao_de_pagamento",
        "compras_faturadas",
    ]

"""Regressões da auditoria: D2, D3 e D4.

D2 — 1P ativo não suprime o gargalo logístico nem silencia a ação.
D3 — a ação que resolve um gargalo não é bloqueada por ele.
D4 — redução de preço passa pelo piso de rentabilidade (guardrail #6).
"""

from __future__ import annotations

from datetime import date

from kam_agent.agents.graph import _recomendar
from kam_agent.domain.enums import (
    ResultadoGuardrail,
    TipoGargalo,
    TipoRecomendacao,
)
from kam_agent.domain.guardrails import classificar_gargalo, consolidar_top3, guardrails_da_acao
from kam_agent.domain.models import PerformanceSKU
from kam_agent.domain.price_simulation import simular_reducao_para_vencedor


def _registro(**extra: object) -> PerformanceSKU:
    base: dict[str, object] = {
        "data": date(2026, 11, 14),
        "id_seller": "10024",
        "sku_pai": "P1",
        "sku_filho": "F1",
    }
    base.update(extra)
    return PerformanceSKU(**base)


def _gargalo_logistico(**extra: object) -> PerformanceSKU:
    base: dict[str, object] = {
        "preco_por": 100.0,
        "winner_avg_price": 100.0,
        "delta_preco": 0.0,
        "buybox_win_rate": 0.2,
        "delta_prazo": 3.0,
        "categoria_curva": "B",
        "tem_1p": False,
        "receita_faturada": 1000.0,
    }
    base.update(extra)
    return _registro(**base)


# --- D2: 1P ativo com gargalo logístico ------------------------------------


def test_1p_nao_suprime_gargalo_logistico() -> None:
    registro = _gargalo_logistico(tem_1p=True)
    assert classificar_gargalo(registro) is TipoGargalo.LOGISTICA_PRAZO_FRETE


def test_1p_ativo_emite_recomendacao_logistica_nao_bloqueada() -> None:
    registro = _gargalo_logistico(tem_1p=True)
    recomendacao = _recomendar(registro, classificar_gargalo(registro), 1000.0)
    assert recomendacao is not None
    assert recomendacao.tipo is TipoRecomendacao.AJUSTE_FRETE_PRAZO
    assert recomendacao.bloqueada is False


def test_1p_ativo_e_sinalizado_nos_guardrails_da_acao() -> None:
    registro = _gargalo_logistico(tem_1p=True)
    guardrails = guardrails_da_acao(registro, TipoRecomendacao.AJUSTE_FRETE_PRAZO)
    assert any(g.guardrail == "trava_1p" for g in guardrails)


def test_1p_ativo_nunca_entrega_reducao_de_preco_ao_seller() -> None:
    """A recomendação pode ser gerada para auditoria, mas nunca sobrevive ao Top 3."""
    registro = _gargalo_logistico(
        tem_1p=True, delta_preco=10.0, preco_por=110.0, buybox_win_rate=0.3
    )
    recomendacao = _recomendar(registro, classificar_gargalo(registro), 1000.0)
    if recomendacao is not None and recomendacao.tipo is TipoRecomendacao.REDUCAO_PRECO:
        assert recomendacao.bloqueada is True
        assert consolidar_top3([recomendacao]) == ()


# --- D3: a ação que resolve o gargalo não é bloqueada por ele --------------


def test_recomendacao_de_frete_sobrevive_ao_top3() -> None:
    registro = _gargalo_logistico()
    recomendacao = _recomendar(registro, classificar_gargalo(registro), 1000.0)
    assert recomendacao is not None
    assert len(consolidar_top3([recomendacao])) == 1


def test_gargalo_de_funil_nao_bloqueia_a_propria_acao_de_funil() -> None:
    registro = _registro(
        cliques=100,
        adicao_ao_carrinho=100,
        adicao_de_informacoes_de_envio=20,
        adicao_de_pagamento=18,
        compras_faturadas=15,
        categoria_curva="B",
        tem_1p=False,
        buybox_win_rate=0.9,
        delta_preco=0.0,
        delta_prazo=0.0,
    )
    assert classificar_gargalo(registro) is TipoGargalo.ATRITO_CHECKOUT
    recomendacao = _recomendar(registro, TipoGargalo.ATRITO_CHECKOUT, 1000.0)
    assert recomendacao is not None
    assert recomendacao.bloqueada is False


# --- D4: piso de rentabilidade na redução de preço -------------------------


def test_reducao_de_preco_sem_margem_e_bloqueada() -> None:
    """Custo alto: reduzir ao vencedor derruba a rentabilidade abaixo de 5%."""
    registro = _registro(
        preco_por=100.0,
        winner_avg_price=50.0,
        delta_preco=50.0,
        buybox_win_rate=0.3,
        percentual_de_comissao=0.2,
        unidades_vendidas=10.0,
        margem=100.0,
        receita_faturada=1000.0,
        categoria_curva="B",
        tem_1p=False,
    )
    # A simulação isolada reprova...
    assert simular_reducao_para_vencedor(registro).resultado is ResultadoGuardrail.BLOQUEADO

    # ...e o guardrail da ação agora propaga essa reprovação.
    recomendacao = _recomendar(registro, TipoGargalo.PRECO_ACIMA_CONCORRENTE, 1000.0)
    assert recomendacao is not None
    assert recomendacao.bloqueada is True
    assert any(g.guardrail == "piso_rentabilidade" for g in recomendacao.guardrails)
    assert consolidar_top3([recomendacao]) == ()


def test_reducao_de_preco_com_margem_permanece_aprovada() -> None:
    """Custo baixo: a redução preserva rentabilidade acima do piso."""
    registro = _registro(
        preco_por=100.0,
        winner_avg_price=90.0,
        delta_preco=10.0,
        buybox_win_rate=0.3,
        percentual_de_comissao=0.2,
        unidades_vendidas=10.0,
        margem=300.0,
        receita_faturada=1000.0,
        categoria_curva="B",
        tem_1p=False,
    )
    recomendacao = _recomendar(registro, TipoGargalo.PRECO_ACIMA_CONCORRENTE, 1000.0)
    assert recomendacao is not None
    assert recomendacao.bloqueada is False
    assert len(consolidar_top3([recomendacao])) == 1

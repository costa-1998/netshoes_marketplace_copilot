"""Classificação de gargalo (task 7.2)."""

from __future__ import annotations

from datetime import date

from kam_agent.domain.enums import TipoGargalo
from kam_agent.domain.models import PerformanceSKU
from kam_agent.tools.gargalo import gargalo_do_sku


def _registro(**extra: object) -> PerformanceSKU:
    base: dict[str, object] = {
        "data": date(2026, 11, 14),
        "id_seller": "10024",
        "sku_pai": "P1",
    }
    base.update(extra)
    return PerformanceSKU(**base)


def test_sku_pai_resulta_nao_avaliavel() -> None:
    registro = _registro(granularidade="sku_pai", categoria_curva="A", cobertura=1.0, tem_1p=True)
    assert gargalo_do_sku(registro) is TipoGargalo.NAO_AVALIAVEL


def test_ruptura_curva_a_tem_prioridade() -> None:
    registro = _registro(sku_filho="F1", categoria_curva="A", cobertura=2.0, tem_1p=False)
    assert gargalo_do_sku(registro) is TipoGargalo.RUPTURA_CURVA_A


def test_trava_1p_identificada() -> None:
    registro = _registro(sku_filho="F1", categoria_curva="B", tem_1p=True)
    assert gargalo_do_sku(registro) is TipoGargalo.TRAVA_1P


def test_sem_gargalo() -> None:
    registro = _registro(
        sku_filho="F1",
        categoria_curva="B",
        tem_1p=False,
        buybox_win_rate=0.9,
        delta_preco=0.0,
        delta_prazo=0.0,
        compras_faturadas=75,
        cancelamentos=0,
        cliques=100,
        adicao_ao_carrinho=90,
        adicao_de_informacoes_de_envio=85,
        adicao_de_pagamento=80,
    )
    assert gargalo_do_sku(registro) is TipoGargalo.NENHUM

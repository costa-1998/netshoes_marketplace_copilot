"""Priorização preço vs. logística na Buy Box (task 3.3)."""

from __future__ import annotations

from datetime import date

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.guardrails import avaliar_buybox_preco_vs_logistica
from kam_agent.domain.models import PerformanceSKU


def _registro(**extra: object) -> PerformanceSKU:
    base: dict[str, object] = {
        "data": date(2026, 11, 14),
        "id_seller": "10024",
        "sku_pai": "P1",
        "sku_filho": "F1",
    }
    base.update(extra)
    return PerformanceSKU(**base)


def test_preco_competitivo_buybox_baixa_e_prazo_pior_e_logistica() -> None:
    resultado = avaliar_buybox_preco_vs_logistica(
        _registro(delta_preco=0.0, buybox_win_rate=0.3, delta_prazo=2.0)
    )
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO
    assert "logístico" in resultado.motivo


def test_preco_acima_com_margem_permite_reducao() -> None:
    resultado = avaliar_buybox_preco_vs_logistica(
        _registro(delta_preco=10.0, buybox_win_rate=0.3, delta_prazo=1.0)
    )
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_win_rate_ausente_nao_avaliavel() -> None:
    resultado = avaliar_buybox_preco_vs_logistica(_registro(delta_preco=10.0, buybox_win_rate=None))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


def test_delta_preco_ausente_nao_avaliavel() -> None:
    resultado = avaliar_buybox_preco_vs_logistica(_registro(delta_preco=None, buybox_win_rate=0.3))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL

"""Trava anti-canibalização 1P (task 3.2)."""

from __future__ import annotations

from datetime import date

import pytest

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.guardrails import avaliar_trava_1p
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


def test_1p_ativo_preco_acima_bloqueia() -> None:
    resultado = avaliar_trava_1p(_registro(tem_1p=True, preco_por=100.0, winner_avg_price=90.0))
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO
    assert "redução de preço" in resultado.motivo


def test_1p_ativo_gargalo_logistico_nao_bloqueia_preco_competitivo() -> None:
    resultado = avaliar_trava_1p(_registro(tem_1p=True, preco_por=90.0, winner_avg_price=90.0))
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_1p_inativo_nao_bloqueia() -> None:
    resultado = avaliar_trava_1p(_registro(tem_1p=False, preco_por=100.0, winner_avg_price=90.0))
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_1p_desconhecido_nao_avaliavel() -> None:
    resultado = avaliar_trava_1p(_registro(tem_1p=None))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


@pytest.mark.parametrize("tem_1p", [None, True, False])
def test_guardrail_sempre_identificado(tem_1p: bool | None) -> None:
    assert avaliar_trava_1p(_registro(tem_1p=tem_1p)).guardrail == "trava_1p"

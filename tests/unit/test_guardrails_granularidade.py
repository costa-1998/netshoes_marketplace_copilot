"""Regra de granularidade (task 3.1)."""

from __future__ import annotations

from datetime import date

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.guardrails import avaliar_granularidade
from kam_agent.domain.models import PerformanceSKU


def _registro(**extra: object) -> PerformanceSKU:
    base: dict[str, object] = {
        "data": date(2026, 11, 14),
        "id_seller": "10024",
        "sku_pai": "P1",
    }
    base.update(extra)
    return PerformanceSKU(**base)


def test_registro_sku_filho_aprovado() -> None:
    resultado = avaliar_granularidade(_registro(sku_filho="F1"))
    assert resultado.resultado is ResultadoGuardrail.APROVADO
    assert "F1" in resultado.motivo


def test_registro_sku_pai_nao_avaliavel() -> None:
    resultado = avaliar_granularidade(_registro(granularidade="sku_pai"))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL
    assert "P1" in resultado.motivo

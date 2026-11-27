"""Proteção contra ruptura em Curva A (task 3.4)."""

from __future__ import annotations

from datetime import date

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.guardrails import avaliar_ruptura_curva_a
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


def test_curva_a_cobertura_no_limite_bloqueia() -> None:
    resultado = avaliar_ruptura_curva_a(_registro(categoria_curva="A", cobertura=3.0))
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO
    assert "reposição" in resultado.motivo


def test_curva_a_cobertura_suficiente_aprovado() -> None:
    resultado = avaliar_ruptura_curva_a(_registro(categoria_curva="A", cobertura=10.0))
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_curva_b_nao_se_aplica() -> None:
    resultado = avaliar_ruptura_curva_a(_registro(categoria_curva="B", cobertura=1.0))
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_curva_ausente_nao_avaliavel() -> None:
    resultado = avaliar_ruptura_curva_a(_registro(categoria_curva=None, cobertura=1.0))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


def test_curva_a_sem_cobertura_nao_avaliavel() -> None:
    resultado = avaliar_ruptura_curva_a(_registro(categoria_curva="A", cobertura=None))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL

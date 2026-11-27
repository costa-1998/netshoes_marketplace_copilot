"""Piso de rentabilidade na simulação de preço (task 3.6).

Os registros são construídos a partir de um custo unitário conhecido:
``custo = preco_por * (1 - comissao) - margem / unidades``.
"""

from __future__ import annotations

from datetime import date

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.models import PerformanceSKU
from kam_agent.domain.price_simulation import simular_reducao_para_vencedor


def _registro(
    preco_por: float,
    winner: float,
    custo_unitario: float,
    comissao: float = 0.2,
    unidades: float = 10.0,
) -> PerformanceSKU:
    margem = (preco_por * (1 - comissao) - custo_unitario) * unidades
    return PerformanceSKU(
        data=date(2026, 11, 14),
        id_seller="10024",
        sku_pai="P1",
        sku_filho="F1",
        preco_por=preco_por,
        winner_avg_price=winner,
        percentual_de_comissao=comissao,
        unidades_vendidas=unidades,
        margem=margem,
        receita_faturada=preco_por * unidades,
        rentabilidade=margem / (preco_por * unidades),
    )


def test_reducao_mantem_rentabilidade_aceita() -> None:
    # Custo 50: a 90, margem = 90*0.8-50 = 22 -> 24,4% de rentabilidade.
    resultado = simular_reducao_para_vencedor(_registro(100.0, 90.0, 50.0))
    assert resultado.resultado is ResultadoGuardrail.APROVADO
    assert resultado.rentabilidade_projetada is not None
    assert resultado.rentabilidade_projetada > 0.05


def test_reducao_viola_piso_rejeita() -> None:
    # Custo 70: a 90, margem = 72-70 = 2 -> 2,2% < 5%.
    resultado = simular_reducao_para_vencedor(_registro(100.0, 90.0, 70.0))
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO
    assert "piso" in resultado.motivo


def test_piso_exato_rejeita() -> None:
    # Custo 68,4: a 90, margem = 72-68,4 = 3,6 -> exatamente 4% ... usar 72-4.5
    # Para 5% exato: custo = 90*0.8 - 0.05*90 = 72 - 4.5 = 67.5
    resultado = simular_reducao_para_vencedor(_registro(100.0, 90.0, 67.5))
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO


def test_comissao_ausente_nao_avaliavel() -> None:
    registro = _registro(100.0, 90.0, 50.0).model_copy(update={"percentual_de_comissao": None})
    resultado = simular_reducao_para_vencedor(registro)
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


def test_margem_ausente_nao_avaliavel() -> None:
    registro = _registro(100.0, 90.0, 50.0).model_copy(update={"margem": None})
    resultado = simular_reducao_para_vencedor(registro)
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


def test_preco_vencedor_ausente_nao_avaliavel() -> None:
    registro = _registro(100.0, 90.0, 50.0).model_copy(update={"winner_avg_price": None})
    resultado = simular_reducao_para_vencedor(registro)
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


def test_preco_ja_competitivo_sem_reducao() -> None:
    resultado = simular_reducao_para_vencedor(_registro(90.0, 95.0, 50.0))
    assert resultado.resultado is ResultadoGuardrail.APROVADO
    assert resultado.preco_projetado == 90.0

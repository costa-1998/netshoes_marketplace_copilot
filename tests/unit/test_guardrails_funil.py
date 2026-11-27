"""Diagnóstico de funil e cancelamento (task 3.5).

A fixture é monotônica, então a queda acentuada é exercitada com registro
sintético.
"""

from __future__ import annotations

from datetime import date

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.guardrails import diagnosticar_cancelamento, diagnosticar_funil
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


def _funil(
    cliques: float, carrinho: float, envio: float, pagamento: float, faturadas: float
) -> PerformanceSKU:
    return _registro(
        cliques=cliques,
        adicao_ao_carrinho=carrinho,
        adicao_de_informacoes_de_envio=envio,
        adicao_de_pagamento=pagamento,
        compras_faturadas=faturadas,
    )


def test_queda_acentuada_bloqueia_e_identifica_etapa() -> None:
    # Queda de 80% entre carrinho e envio.
    resultado = diagnosticar_funil(_funil(100, 100, 20, 18, 15))
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO
    assert "adicao_de_informacoes_de_envio" in resultado.motivo


def test_funil_saudavel_aprovado() -> None:
    resultado = diagnosticar_funil(_funil(100, 90, 85, 80, 75))
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_etapa_ausente_nao_avaliavel() -> None:
    resultado = diagnosticar_funil(_funil(100, 90, 85, 80, None))  # type: ignore[arg-type]
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL


def test_sessoes_nao_participa_da_comparacao() -> None:
    # sessoes menor que cliques não gera atrito falso.
    resultado = diagnosticar_funil(
        _registro(
            sessoes=10,
            cliques=100,
            adicao_ao_carrinho=90,
            adicao_de_informacoes_de_envio=85,
            adicao_de_pagamento=80,
            compras_faturadas=75,
        )
    )
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_cancelamento_acima_do_limite_bloqueia() -> None:
    resultado = diagnosticar_cancelamento(_registro(compras_faturadas=10, cancelamentos=3))
    assert resultado.resultado is ResultadoGuardrail.BLOQUEADO


def test_cancelamento_dentro_do_limite_aprovado() -> None:
    resultado = diagnosticar_cancelamento(_registro(compras_faturadas=10, cancelamentos=1))
    assert resultado.resultado is ResultadoGuardrail.APROVADO


def test_cancelamento_sem_vendas_nao_avaliavel() -> None:
    resultado = diagnosticar_cancelamento(_registro(compras_faturadas=0, cancelamentos=0))
    assert resultado.resultado is ResultadoGuardrail.NAO_AVALIAVEL

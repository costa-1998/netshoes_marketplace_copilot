"""Testes dos contratos Pydantic do domínio (task 2.2)."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from kam_agent.domain.enums import Granularidade, ResultadoGuardrail, TipoRecomendacao
from kam_agent.domain.models import (
    PerformanceSKU,
    Recomendacao,
    ResultadoGuardrailDetalhado,
)


def _base(**extra: object) -> dict[str, Any]:
    dados: dict[str, Any] = {
        "data": date(2026, 11, 14),
        "id_seller": "10024",
        "sku_pai": "C79-1588-010",
    }
    dados.update(extra)
    return dados


def test_sku_filho_sem_identificador_e_rejeitado() -> None:
    with pytest.raises(ValidationError):
        PerformanceSKU(**_base(granularidade="sku_filho"))


def test_sku_pai_sem_sku_filho_e_aceito() -> None:
    registro = PerformanceSKU(**_base(granularidade="sku_pai"))
    assert registro.granularidade is Granularidade.SKU_PAI
    assert registro.sku_filho is None
    assert registro.exige_sku_filho is False


def test_sku_filho_completo_e_aceito() -> None:
    registro = PerformanceSKU(**_base(sku_filho="C79-1588-010-38"))
    assert registro.granularidade is Granularidade.SKU_FILHO
    assert registro.exige_sku_filho is True


def test_metricas_sao_opcionais() -> None:
    registro = PerformanceSKU(**_base(sku_filho="X-1"))
    assert registro.preco_por is None
    assert registro.buybox_win_rate is None


def test_campo_desconhecido_e_rejeitado() -> None:
    with pytest.raises(ValidationError):
        PerformanceSKU(**_base(sku_filho="X-1", campo_inventado=1))


def test_recomendacao_bloqueada_por_guardrail() -> None:
    aprovado = ResultadoGuardrailDetalhado(
        guardrail="granularidade",
        resultado=ResultadoGuardrail.APROVADO,
        motivo="ok",
    )
    bloqueado = ResultadoGuardrailDetalhado(
        guardrail="trava_1p",
        resultado=ResultadoGuardrail.BLOQUEADO,
        motivo="1P ativo",
    )
    recomendacao = Recomendacao(
        tipo=TipoRecomendacao.REDUCAO_PRECO,
        impacto_financeiro_estimado=100.0,
        justificativa="teste",
        sku_pai="P",
        guardrails=(aprovado, bloqueado),
    )
    assert recomendacao.bloqueada is True

    liberada = Recomendacao(
        tipo=TipoRecomendacao.REPOSICAO_ESTOQUE,
        impacto_financeiro_estimado=100.0,
        justificativa="teste",
        sku_pai="P",
        guardrails=(aprovado,),
    )
    assert liberada.bloqueada is False

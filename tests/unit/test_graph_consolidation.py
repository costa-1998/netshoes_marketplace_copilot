"""Consolidação no grafo: bloqueadas removidas e Top 3 (task 8.5)."""

from __future__ import annotations

from kam_agent.agents.graph import no_consolidar
from kam_agent.agents.state import EstadoAgente
from kam_agent.domain.enums import ResultadoGuardrail, TipoRecomendacao
from kam_agent.domain.models import Recomendacao, ResultadoGuardrailDetalhado

_APROVADO = ResultadoGuardrailDetalhado(
    guardrail="granularidade", resultado=ResultadoGuardrail.APROVADO, motivo="ok"
)
_BLOQUEADO = ResultadoGuardrailDetalhado(
    guardrail="trava_1p", resultado=ResultadoGuardrail.BLOQUEADO, motivo="1P"
)


def _rec(sku: str, impacto: float, guardrails=(_APROVADO,)) -> Recomendacao:
    return Recomendacao(
        tipo=TipoRecomendacao.REPOSICAO_ESTOQUE,
        impacto_financeiro_estimado=impacto,
        justificativa="teste",
        sku_pai=sku,
        guardrails=tuple(guardrails),
    )


def _estado(recs: tuple[Recomendacao, ...]) -> EstadoAgente:
    return {
        "id_seller": "10024",
        "mensagem": "x",
        "correlation_id": "c",
        "recomendacoes": recs,
    }


def test_remove_bloqueadas_e_aplica_top3() -> None:
    recs = (
        _rec("S1", 100.0, (_BLOQUEADO,)),
        _rec("S2", 90.0),
        _rec("S3", 80.0),
        _rec("S4", 70.0),
        _rec("S5", 60.0),
    )
    resultado = no_consolidar(_estado(recs))
    skus = [r.sku_pai for r in resultado["recomendacoes"]]
    assert "S1" not in skus
    assert skus == ["S2", "S3", "S4"]


def test_sem_aprovadas_explica_ausencia() -> None:
    resultado = no_consolidar(_estado((_rec("S1", 10.0, (_BLOQUEADO,)),)))
    assert resultado["recomendacoes"] == ()
    assert "bloqueada" in resultado["resposta"]


def test_erro_previo_preserva_resposta() -> None:
    estado: EstadoAgente = {
        "id_seller": "10024",
        "mensagem": "x",
        "correlation_id": "c",
        "erro": "falhou",
        "resposta": "mensagem de erro",
    }
    assert no_consolidar(estado) == {}

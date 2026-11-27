"""Consolidação Top 3 com desempate determinístico (task 3.7)."""

from __future__ import annotations

from kam_agent.domain.enums import ResultadoGuardrail, TipoRecomendacao
from kam_agent.domain.guardrails import consolidar_top3
from kam_agent.domain.models import Recomendacao, ResultadoGuardrailDetalhado

_APROVADO = ResultadoGuardrailDetalhado(
    guardrail="granularidade", resultado=ResultadoGuardrail.APROVADO, motivo="ok"
)
_BLOQUEADO = ResultadoGuardrailDetalhado(
    guardrail="trava_1p", resultado=ResultadoGuardrail.BLOQUEADO, motivo="1P"
)
_NAO_AVALIAVEL = ResultadoGuardrailDetalhado(
    guardrail="curva", resultado=ResultadoGuardrail.NAO_AVALIAVEL, motivo="sem curva"
)


def _rec(sku: str, impacto: float, guardrails=(_APROVADO,)) -> Recomendacao:
    return Recomendacao(
        tipo=TipoRecomendacao.REPOSICAO_ESTOQUE,
        impacto_financeiro_estimado=impacto,
        justificativa="teste",
        sku_pai=sku,
        guardrails=tuple(guardrails),
    )


def test_mais_de_tres_retorna_top3() -> None:
    candidatas = [_rec(f"S{i}", float(i)) for i in range(1, 6)]
    resultado = consolidar_top3(candidatas)
    assert len(resultado) == 3
    assert [r.impacto_financeiro_estimado for r in resultado] == [5.0, 4.0, 3.0]


def test_empate_na_fronteira_e_estavel() -> None:
    candidatas = [_rec("S1", 10.0), _rec("S2", 5.0), _rec("S3", 5.0), _rec("S0", 1.0)]
    primeira = consolidar_top3(candidatas)
    segunda = consolidar_top3(list(reversed(candidatas)))
    assert [r.sku_pai for r in primeira] == [r.sku_pai for r in segunda]
    assert [r.sku_pai for r in primeira] == ["S1", "S2", "S3"]


def test_zero_candidatas() -> None:
    assert consolidar_top3([]) == ()


def test_bloqueadas_e_nao_avaliaveis_nunca_ocupam_vaga() -> None:
    candidatas = [
        _rec("S1", 100.0, (_BLOQUEADO,)),
        _rec("S2", 90.0, (_NAO_AVALIAVEL,)),
        _rec("S3", 80.0),
        _rec("S4", 70.0),
    ]
    resultado = consolidar_top3(candidatas)
    assert [r.sku_pai for r in resultado] == ["S3", "S4"]


def test_apenas_aprovadas_quando_todas_bloqueadas() -> None:
    candidatas = [_rec("S1", 100.0, (_BLOQUEADO,)), _rec("S2", 90.0, (_NAO_AVALIAVEL,))]
    assert consolidar_top3(candidatas) == ()

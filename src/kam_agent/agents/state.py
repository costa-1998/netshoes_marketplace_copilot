"""Estado tipado do grafo de orquestração."""

from __future__ import annotations

from typing import NotRequired, TypedDict

from kam_agent.domain.models import PerformanceSKU, Recomendacao, ResultadoGuardrailDetalhado


class EstadoAgente(TypedDict):
    """Estado transportado entre nós do grafo.

    ``id_seller`` é obrigatório: sem ele o fluxo não consulta dados.
    """

    id_seller: str
    mensagem: str
    correlation_id: str
    especialista: NotRequired[str | None]
    registros: NotRequired[tuple[PerformanceSKU, ...]]
    recomendacoes: NotRequired[tuple[Recomendacao, ...]]
    guardrails: NotRequired[tuple[ResultadoGuardrailDetalhado, ...]]
    resposta: NotRequired[str | None]
    erro: NotRequired[str | None]


CAMPOS_OBRIGATORIOS: tuple[str, ...] = ("id_seller", "mensagem", "correlation_id")


def validar_estado(estado: EstadoAgente) -> list[str]:
    """Lista os campos obrigatórios ausentes no estado."""
    ausentes: list[str] = []
    for campo in CAMPOS_OBRIGATORIOS:
        if not estado.get(campo):
            ausentes.append(campo)
    return ausentes

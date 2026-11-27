"""Grafo de orquestração LangGraph, executável offline (D9).

Fluxo: validar estado → rotear → especialista substituto → consolidar.
O nó de especialista não chama LLM; a troca para Vertex AI fica restrita ao
corpo de ``no_especialista``.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from langgraph.graph import END, START, StateGraph

from kam_agent.agents.router import ESPECIALISTA_PADRAO, gargalos_por_especialista, rotear
from kam_agent.agents.state import EstadoAgente, validar_estado
from kam_agent.domain.enums import TipoGargalo, TipoRecomendacao
from kam_agent.domain.guardrails import (
    avaliar_todos,
    classificar_gargalo,
    consolidar_top3,
    guardrails_da_acao,
)
from kam_agent.domain.models import PerformanceSKU, Recomendacao
from kam_agent.ports.seller_data import SellerDataPort
from kam_agent.tools.seller_performance import resumir_performance

logger = logging.getLogger(__name__)

#: Impacto estimado por tipo de gargalo, usado pelo especialista substituto.
_IMPACTO_POR_GARGALO: dict[TipoGargalo, float] = {
    TipoGargalo.RUPTURA_CURVA_A: 5000.0,
    TipoGargalo.LOGISTICA_PRAZO_FRETE: 3000.0,
    TipoGargalo.PRECO_ACIMA_CONCORRENTE: 2500.0,
    TipoGargalo.CANCELAMENTO_ALTO: 2000.0,
    TipoGargalo.ATRITO_CHECKOUT: 1500.0,
    TipoGargalo.TRAVA_1P: 1000.0,
}

_RECOMENDACAO_POR_GARGALO: dict[TipoGargalo, TipoRecomendacao] = {
    TipoGargalo.RUPTURA_CURVA_A: TipoRecomendacao.REPOSICAO_ESTOQUE,
    TipoGargalo.LOGISTICA_PRAZO_FRETE: TipoRecomendacao.AJUSTE_FRETE_PRAZO,
    TipoGargalo.PRECO_ACIMA_CONCORRENTE: TipoRecomendacao.REDUCAO_PRECO,
    TipoGargalo.CANCELAMENTO_ALTO: TipoRecomendacao.INVESTIGAR_CANCELAMENTO,
    TipoGargalo.ATRITO_CHECKOUT: TipoRecomendacao.AJUSTE_FUNIL,
}


def _impacto(registro: PerformanceSKU, gargalo: TipoGargalo, receita_janela: float) -> float:
    base = _IMPACTO_POR_GARGALO.get(gargalo, 0.0)
    return base + receita_janela


def _recomendar(
    registro: PerformanceSKU, gargalo: TipoGargalo, receita_janela: float
) -> Recomendacao | None:
    """Recomendação por SKU, com impacto acumulado na janela.

    A janela traz um registro por dia; a recomendação é por SKU filho, então
    o impacto soma a receita do período em vez de contar cada dia como uma
    recomendação distinta.
    """
    tipo = _RECOMENDACAO_POR_GARGALO.get(gargalo)
    if tipo is None:
        return None
    return Recomendacao(
        tipo=tipo,
        impacto_financeiro_estimado=_impacto(registro, gargalo, receita_janela),
        justificativa=(
            f"Gargalo {gargalo.value} identificado no SKU {registro.sku_filho or registro.sku_pai}."
        ),
        sku_pai=registro.sku_pai,
        sku_filho=registro.sku_filho,
        gargalo=gargalo,
        guardrails=guardrails_da_acao(registro, tipo),
    )


def no_validar(estado: EstadoAgente) -> dict[str, Any]:
    """Interrompe o fluxo quando faltam campos obrigatórios."""
    ausentes = validar_estado(estado)
    if ausentes:
        return {
            "erro": f"Estado inválido: campos obrigatórios ausentes ({', '.join(ausentes)}).",
            "resposta": "Não foi possível processar: contexto de seller ausente.",
        }
    return {"erro": None}


def no_rotear(estado: EstadoAgente) -> dict[str, Any]:
    """Seleciona o especialista por intenção."""
    if estado.get("erro"):
        return {}
    return {"especialista": rotear(estado["mensagem"])}


def no_especialista(
    estado: EstadoAgente, porta: SellerDataPort, data_referencia: date
) -> dict[str, Any]:
    """Especialista substituto: analisa registros e propõe recomendações."""
    if estado.get("erro"):
        return {}

    especialista = estado.get("especialista") or ESPECIALISTA_PADRAO

    # O seller vem do estado da execução (a ferramenta não aceita id_seller).
    registros = resumir_performance(porta, estado, data_referencia)

    gargalos_relevantes = gargalos_por_especialista(especialista)

    # Agrega a janela por SKU filho: o registro mais recente representa o SKU
    # e a receita do período entra no impacto.
    por_sku: dict[str, tuple[PerformanceSKU, float]] = {}
    for registro in registros:
        chave = registro.sku_filho or registro.sku_pai
        receita = registro.receita_faturada or 0.0
        anterior = por_sku.get(chave)
        if anterior is None or registro.data > anterior[0].data:
            por_sku[chave] = (registro, (anterior[1] if anterior else 0.0) + receita)
        else:
            por_sku[chave] = (anterior[0], anterior[1] + receita)

    recomendacoes: list[Recomendacao] = []
    for registro, receita_janela in por_sku.values():
        gargalo = classificar_gargalo(registro)
        if gargalos_relevantes and gargalo not in gargalos_relevantes:
            continue
        recomendacao = _recomendar(registro, gargalo, receita_janela)
        if recomendacao is not None:
            recomendacoes.append(recomendacao)

    return {
        "registros": registros,
        "recomendacoes": tuple(recomendacoes),
        "guardrails": tuple(g for registro in registros for g in avaliar_todos(registro)),
    }


def no_consolidar(estado: EstadoAgente) -> dict[str, Any]:
    """Remove bloqueadas, aplica Top 3 e monta a resposta final."""
    if estado.get("erro"):
        return {}

    recomendacoes = estado.get("recomendacoes") or ()
    top3 = consolidar_top3(recomendacoes)
    total_bloqueadas = sum(1 for r in recomendacoes if r.bloqueada)

    if not top3:
        resposta = (
            "Nenhuma recomendação elegível para este seller no período. "
            f"{total_bloqueadas} recomendação(ões) bloqueada(s) por guardrail."
        )
    else:
        linhas = [
            f"{i}. {r.tipo.value} — SKU {r.sku_filho or r.sku_pai} "
            f"(impacto estimado R$ {r.impacto_financeiro_estimado:,.2f})"
            for i, r in enumerate(top3, start=1)
        ]
        resposta = "Top recomendações:\n" + "\n".join(linhas)

    # A presença de 1P é sinalizada ao seller mesmo quando não gera ação:
    # ela explica por que aquele SKU filho não recebeu recomendação de preço.
    skus_1p = sorted(
        {r.sku_filho or r.sku_pai for r in (estado.get("registros") or ()) if r.tem_1p}
    )
    if skus_1p:
        resposta += (
            f"\n\nAtenção: {len(skus_1p)} SKU(s) filho com estoque 1P ativo "
            f"({', '.join(skus_1p[:5])}{'…' if len(skus_1p) > 5 else ''}). "
            "Esses itens não recebem recomendação de preço para não disputar a "
            "Buy Box contra a própria Netshoes."
        )

    return {"recomendacoes": top3, "resposta": resposta}


def _apos_validar(estado: EstadoAgente) -> str:
    return "consolidar" if estado.get("erro") else "rotear"


def construir_grafo(porta: SellerDataPort, data_referencia: date):
    """Monta e compila o ``StateGraph`` do copiloto."""

    grafo = StateGraph(EstadoAgente)
    grafo.add_node("validar", no_validar)
    grafo.add_node("rotear", no_rotear)
    grafo.add_node(
        "especialista",
        lambda estado: no_especialista(estado, porta, data_referencia),
    )
    grafo.add_node("consolidar", no_consolidar)

    grafo.add_edge(START, "validar")
    grafo.add_conditional_edges(
        "validar", _apos_validar, {"rotear": "rotear", "consolidar": "consolidar"}
    )
    grafo.add_edge("rotear", "especialista")
    grafo.add_edge("especialista", "consolidar")
    grafo.add_edge("consolidar", END)

    return grafo.compile()


def executar(
    porta: SellerDataPort,
    id_seller: str,
    mensagem: str,
    correlation_id: str,
    data_referencia: date,
) -> EstadoAgente:
    """Executa o grafo com estado inicial e devolve o estado final."""
    estado_inicial: EstadoAgente = {
        "id_seller": id_seller,
        "mensagem": mensagem,
        "correlation_id": correlation_id,
    }
    try:
        return construir_grafo(porta, data_referencia).invoke(estado_inicial)
    except Exception as exc:  # noqa: BLE001 - falha vira estado, não exceção bruta
        logger.exception("Falha na execução do grafo (correlation_id=%s)", correlation_id)
        return {
            **estado_inicial,
            "erro": "Falha interna ao processar a solicitação.",
            "resposta": "Não foi possível concluir a análise.",
            "correlation_id": correlation_id,
            "_excecao": type(exc).__name__,
        }

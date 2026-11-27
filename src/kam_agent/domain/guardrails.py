"""Regras de guardrail como funções puras.

Cada regra devolve :class:`ResultadoGuardrailDetalhado` com um de três
estados — ``APROVADO``, ``BLOQUEADO`` ou ``NAO_AVALIAVEL`` (D2). Ausência de
dado nunca vira aprovação silenciosa.
"""

from __future__ import annotations

from collections.abc import Sequence

from kam_agent.domain.enums import (
    EtapaFunil,
    ResultadoGuardrail,
    TipoGargalo,
    TipoRecomendacao,
)
from kam_agent.domain.models import PerformanceSKU, ResultadoGuardrailDetalhado

#: Piso de rentabilidade exigido pela constituição (guardrail #6).
PISO_RENTABILIDADE = 0.05
#: Cobertura mínima de estoque, em dias, para Curva A.
COBERTURA_MINIMA_CURVA_A = 3.0
#: Taxa de vitória de Buy Box abaixo da qual há perda de Buy Box.
BUYBOX_WIN_RATE_MINIMO = 0.50
#: Razão de cancelamento acima da qual há alerta operacional.
TAXA_CANCELAMENTO_LIMITE = 0.15
#: Queda relativa entre etapas do funil considerada acentuada.
QUEDA_FUNIL_ACENTUADA = 0.30


def _resultado(
    guardrail: str, resultado: ResultadoGuardrail, motivo: str
) -> ResultadoGuardrailDetalhado:
    return ResultadoGuardrailDetalhado(guardrail=guardrail, resultado=resultado, motivo=motivo)


def avaliar_granularidade(registro: PerformanceSKU) -> ResultadoGuardrailDetalhado:
    """Regra base: análise exige SKU filho (guardrail #1)."""
    if registro.exige_sku_filho:
        return _resultado(
            "granularidade",
            ResultadoGuardrail.APROVADO,
            f"Registro no grão de SKU filho '{registro.sku_filho}'.",
        )
    return _resultado(
        "granularidade",
        ResultadoGuardrail.NAO_AVALIAVEL,
        f"Registro do SKU pai '{registro.sku_pai}' não possui SKU filho.",
    )


def avaliar_trava_1p(registro: PerformanceSKU) -> ResultadoGuardrailDetalhado:
    """Trava anti-canibalização 1P (guardrail #2)."""
    if registro.tem_1p is None:
        return _resultado(
            "trava_1p",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Indicador de 1P ativo ausente.",
        )
    if not registro.tem_1p:
        return _resultado("trava_1p", ResultadoGuardrail.APROVADO, "Sem 1P ativo no SKU filho.")
    if registro.preco_por is None or registro.winner_avg_price is None:
        return _resultado(
            "trava_1p",
            ResultadoGuardrail.BLOQUEADO,
            "1P ativo: disputa de Buy Box por preço proibida (preço de referência ausente).",
        )
    if registro.preco_por > registro.winner_avg_price:
        return _resultado(
            "trava_1p",
            ResultadoGuardrail.BLOQUEADO,
            f"1P ativo com preço {registro.preco_por} acima do vencedor "
            f"{registro.winner_avg_price}: redução de preço e campanha proibidas.",
        )
    return _resultado(
        "trava_1p",
        ResultadoGuardrail.APROVADO,
        "1P ativo, mas sem disputa de preço contra o próprio marketplace.",
    )


def avaliar_buybox_preco_vs_logistica(
    registro: PerformanceSKU,
) -> ResultadoGuardrailDetalhado:
    """Priorização preço vs. logística na Buy Box (guardrail #3)."""
    if registro.buybox_win_rate is None:
        return _resultado(
            "buybox_preco_vs_logistica",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Taxa de vitória de Buy Box ausente.",
        )
    if registro.delta_preco is None:
        return _resultado(
            "buybox_preco_vs_logistica",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Desvio de preço ausente.",
        )
    if registro.delta_preco > 0:
        return _resultado(
            "buybox_preco_vs_logistica",
            ResultadoGuardrail.APROVADO,
            f"Preço {registro.delta_preco:.2f} acima do vencedor: redução permitida.",
        )
    if registro.buybox_win_rate < BUYBOX_WIN_RATE_MINIMO:
        delta_prazo = registro.delta_prazo or 0.0
        if delta_prazo > 0:
            return _resultado(
                "buybox_preco_vs_logistica",
                ResultadoGuardrail.BLOQUEADO,
                "Preço competitivo com Buy Box < 50% e prazo acima do vencedor: "
                "gargalo logístico, redução de preço proibida.",
            )
        return _resultado(
            "buybox_preco_vs_logistica",
            ResultadoGuardrail.BLOQUEADO,
            "Preço competitivo com Buy Box < 50%: redução de preço não resolveria.",
        )
    return _resultado(
        "buybox_preco_vs_logistica",
        ResultadoGuardrail.APROVADO,
        "Buy Box saudável para o preço praticado.",
    )


def avaliar_ruptura_curva_a(registro: PerformanceSKU) -> ResultadoGuardrailDetalhado:
    """Proteção contra ruptura em Curva A (guardrail #4)."""
    if registro.categoria_curva is None:
        return _resultado(
            "ruptura_curva_a",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Curva do SKU ausente.",
        )
    if registro.categoria_curva.upper() != "A":
        return _resultado(
            "ruptura_curva_a",
            ResultadoGuardrail.APROVADO,
            f"SKU de Curva {registro.categoria_curva.upper()}: regra não se aplica.",
        )
    if registro.cobertura is None:
        return _resultado(
            "ruptura_curva_a",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Cobertura de estoque ausente para SKU de Curva A.",
        )
    if registro.cobertura <= COBERTURA_MINIMA_CURVA_A:
        return _resultado(
            "ruptura_curva_a",
            ResultadoGuardrail.BLOQUEADO,
            f"Curva A com cobertura de {registro.cobertura:.1f} dias: "
            "redução de preço bloqueada, reposição priorizada.",
        )
    return _resultado(
        "ruptura_curva_a",
        ResultadoGuardrail.APROVADO,
        f"Curva A com cobertura de {registro.cobertura:.1f} dias.",
    )


_ETAPAS_FUNIL: tuple[tuple[EtapaFunil, str], ...] = (
    (EtapaFunil.CLIQUES, "cliques"),
    (EtapaFunil.CARRINHO, "adicao_ao_carrinho"),
    (EtapaFunil.ENVIO, "adicao_de_informacoes_de_envio"),
    (EtapaFunil.PAGAMENTO, "adicao_de_pagamento"),
    (EtapaFunil.FATURADAS, "compras_faturadas"),
)


def _valor_etapa(registro: PerformanceSKU, campo: str) -> float | None:
    valor = getattr(registro, campo, None)
    return float(valor) if valor is not None else None


def diagnosticar_funil(registro: PerformanceSKU) -> ResultadoGuardrailDetalhado:
    """Abandono de funil entre etapas consecutivas (guardrail #5).

    ``sessoes`` fica fora da comparação: a fixture original a trazia menor que
    ``cliques``, e a constituição só exige a cadeia carrinho → faturadas.
    """
    queda_maxima = 0.0
    etapa_queda: str | None = None

    for (_, campo_anterior), (etapa_atual, campo_atual) in zip(
        _ETAPAS_FUNIL, _ETAPAS_FUNIL[1:], strict=False
    ):
        anterior = _valor_etapa(registro, campo_anterior)
        atual = _valor_etapa(registro, campo_atual)
        if anterior is None or atual is None:
            return _resultado(
                "funil",
                ResultadoGuardrail.NAO_AVALIAVEL,
                f"Etapa '{campo_anterior}' ou '{campo_atual}' ausente.",
            )
        if anterior <= 0:
            return _resultado(
                "funil",
                ResultadoGuardrail.NAO_AVALIAVEL,
                f"Etapa '{campo_anterior}' sem volume para calcular conversão.",
            )
        queda = (anterior - atual) / anterior
        if queda > queda_maxima:
            queda_maxima = queda
            etapa_queda = etapa_atual.value

    if etapa_queda is not None and queda_maxima >= QUEDA_FUNIL_ACENTUADA:
        return _resultado(
            "funil",
            ResultadoGuardrail.BLOQUEADO,
            f"Queda de {queda_maxima:.0%} em '{etapa_queda}': atrito de checkout.",
        )
    return _resultado(
        "funil",
        ResultadoGuardrail.APROVADO,
        f"Maior queda entre etapas: {queda_maxima:.0%}.",
    )


def diagnosticar_cancelamento(registro: PerformanceSKU) -> ResultadoGuardrailDetalhado:
    """Cancelamentos sobre compras faturadas (guardrail #5)."""
    faturadas = registro.compras_faturadas
    cancelamentos = registro.cancelamentos
    if faturadas is None or cancelamentos is None:
        return _resultado(
            "cancelamento",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Compras faturadas ou cancelamentos ausentes.",
        )
    if faturadas <= 0:
        return _resultado(
            "cancelamento",
            ResultadoGuardrail.NAO_AVALIAVEL,
            "Sem compras faturadas para calcular a taxa de cancelamento.",
        )
    taxa = cancelamentos / faturadas
    if taxa > TAXA_CANCELAMENTO_LIMITE:
        return _resultado(
            "cancelamento",
            ResultadoGuardrail.BLOQUEADO,
            f"Cancelamentos em {taxa:.1%} das compras: alerta operacional.",
        )
    return _resultado(
        "cancelamento",
        ResultadoGuardrail.APROVADO,
        f"Cancelamentos em {taxa:.1%} das compras.",
    )


def classificar_gargalo(registro: PerformanceSKU) -> TipoGargalo:
    """Gargalo dominante do registro, na ordem de prioridade da constituição.

    A presença de 1P **não** suprime o gargalo real: um SKU com 1P ativo e
    prazo pior tem gargalo logístico, e a trava 1P apenas impede a
    recomendação de preço (guardrail, não diagnóstico).
    """
    if not registro.exige_sku_filho:
        return TipoGargalo.NAO_AVALIAVEL

    if avaliar_ruptura_curva_a(registro).resultado is ResultadoGuardrail.BLOQUEADO:
        return TipoGargalo.RUPTURA_CURVA_A

    buybox = avaliar_buybox_preco_vs_logistica(registro)
    if buybox.resultado is ResultadoGuardrail.BLOQUEADO:
        return TipoGargalo.LOGISTICA_PRAZO_FRETE
    if buybox.resultado is ResultadoGuardrail.APROVADO and (registro.delta_preco or 0) > 0:
        return TipoGargalo.PRECO_ACIMA_CONCORRENTE

    if diagnosticar_cancelamento(registro).resultado is ResultadoGuardrail.BLOQUEADO:
        return TipoGargalo.CANCELAMENTO_ALTO

    if diagnosticar_funil(registro).resultado is ResultadoGuardrail.BLOQUEADO:
        return TipoGargalo.ATRITO_CHECKOUT

    if registro.tem_1p:
        return TipoGargalo.TRAVA_1P

    return TipoGargalo.NENHUM


def avaliar_todos(registro: PerformanceSKU) -> tuple[ResultadoGuardrailDetalhado, ...]:
    """Avalia todos os guardrails aplicáveis a um registro."""
    return (
        avaliar_granularidade(registro),
        avaliar_trava_1p(registro),
        avaliar_buybox_preco_vs_logistica(registro),
        avaliar_ruptura_curva_a(registro),
        diagnosticar_funil(registro),
        diagnosticar_cancelamento(registro),
    )


def guardrails_da_acao(
    registro: PerformanceSKU, tipo: TipoRecomendacao
) -> tuple[ResultadoGuardrailDetalhado, ...]:
    """Guardrails que governam uma ação específica.

    Um bloqueio de redução de preço não pode impedir uma reposição de estoque:
    só as regras pertinentes ao tipo de recomendação entram na decisão. Uma
    ação que *resolve* um gargalo não é bloqueada por ele — só o que a ação
    pode agravar ou o que a proíbe entram na conta.
    """
    granularidade = avaliar_granularidade(registro)

    if tipo is TipoRecomendacao.REDUCAO_PRECO:
        return (
            granularidade,
            avaliar_trava_1p(registro),
            avaliar_buybox_preco_vs_logistica(registro),
            avaliar_ruptura_curva_a(registro),
            _avaliar_piso_rentabilidade(registro),
        )
    if tipo is TipoRecomendacao.AJUSTE_FRETE_PRAZO:
        # A ação corrige o desvio de prazo; o guardrail de Buy Box aponta o
        # gargalo que ela endereça, não um impedimento. A trava 1P entra como
        # sinalização: registra a presença do 1P sem bloquear a logística.
        return (granularidade, avaliar_trava_1p(registro))
    if tipo is TipoRecomendacao.REPOSICAO_ESTOQUE:
        return (granularidade,)
    if tipo is TipoRecomendacao.INVESTIGAR_CANCELAMENTO:
        # O diagnóstico de cancelamento é a razão da ação, não um impedimento.
        return (granularidade,)
    if tipo is TipoRecomendacao.AJUSTE_FUNIL:
        # Idem: a queda no funil origina a ação de ajuste.
        return (granularidade,)
    return (granularidade,)


def _avaliar_piso_rentabilidade(registro: PerformanceSKU) -> ResultadoGuardrailDetalhado:
    """Adapta a simulação de preço ao contrato de resultado de guardrail."""
    from kam_agent.domain.price_simulation import simular_reducao_para_vencedor

    simulacao = simular_reducao_para_vencedor(registro)
    return ResultadoGuardrailDetalhado(
        guardrail="piso_rentabilidade",
        resultado=simulacao.resultado,
        motivo=simulacao.motivo,
    )


def consolidar_top3(
    recomendacoes: Sequence,
    limite: int = 3,
) -> tuple:
    """Consolida até ``limite`` recomendações aprovadas (guardrail #7).

    Desempate determinístico: impacto decrescente, depois ``sku_pai`` e
    ``tipo`` em ordem lexicográfica — estável entre execuções (D2).
    """
    aprovadas = [r for r in recomendacoes if not r.bloqueada]
    ordenadas = sorted(
        aprovadas,
        key=lambda r: (
            -r.impacto_financeiro_estimado,
            r.sku_pai,
            r.sku_filho or "",
            r.tipo.value,
        ),
    )
    return tuple(ordenadas[:limite])

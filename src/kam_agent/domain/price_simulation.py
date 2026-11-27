"""Simulação de preço com piso de rentabilidade (guardrail #6).

Recalcula a rentabilidade projetada ao reduzir ``preco_por`` para
``winner_avg_price``, mantendo o custo unitário e o percentual de comissão
vigentes. Rejeita a simulação quando a rentabilidade projetada não permanece
acima de 5%.
"""

from __future__ import annotations

from kam_agent.domain.enums import ResultadoGuardrail
from kam_agent.domain.guardrails import PISO_RENTABILIDADE
from kam_agent.domain.models import PerformanceSKU, ResultadoGuardrailDetalhado


class ResultadoSimulacaoPreco(ResultadoGuardrailDetalhado):
    """Resultado de guardrail acrescido dos números projetados."""

    preco_projetado: float | None = None
    rentabilidade_projetada: float | None = None
    margem_projetada: float | None = None


def _custo_unitario(registro: PerformanceSKU) -> float | None:
    """Custo unitário implícito, derivado do estado atual do registro.

    ``custo = preco_por * (1 - comissao) - margem / unidades``
    """
    preco = registro.preco_por
    comissao = registro.percentual_de_comissao
    margem = registro.margem
    unidades = registro.unidades_vendidas
    if preco is None or comissao is None or margem is None or not unidades:
        return None
    return preco * (1 - comissao) - margem / unidades


def simular_reducao_para_vencedor(
    registro: PerformanceSKU,
) -> ResultadoSimulacaoPreco:
    """Simula reduzir o preço praticado ao preço de referência vencedor."""
    guardrail = "rentabilidade_simulacao_preco"

    if registro.preco_por is None or registro.winner_avg_price is None:
        return ResultadoSimulacaoPreco(
            guardrail=guardrail,
            resultado=ResultadoGuardrail.NAO_AVALIAVEL,
            motivo="Preço praticado ou preço vencedor ausente.",
        )

    preco_alvo = registro.winner_avg_price
    if preco_alvo >= registro.preco_por:
        return ResultadoSimulacaoPreco(
            guardrail=guardrail,
            resultado=ResultadoGuardrail.APROVADO,
            motivo="Preço praticado já é menor ou igual ao vencedor; sem redução.",
            preco_projetado=registro.preco_por,
        )

    comissao = registro.percentual_de_comissao
    if comissao is None:
        return ResultadoSimulacaoPreco(
            guardrail=guardrail,
            resultado=ResultadoGuardrail.NAO_AVALIAVEL,
            motivo="Percentual de comissão ausente.",
            preco_projetado=preco_alvo,
        )

    custo = _custo_unitario(registro)
    if custo is None:
        return ResultadoSimulacaoPreco(
            guardrail=guardrail,
            resultado=ResultadoGuardrail.NAO_AVALIAVEL,
            motivo="Margem ou unidades vendidas ausentes para derivar o custo.",
            preco_projetado=preco_alvo,
        )

    unidades = registro.unidades_vendidas or 0
    receita_projetada = preco_alvo * unidades
    if receita_projetada <= 0:
        return ResultadoSimulacaoPreco(
            guardrail=guardrail,
            resultado=ResultadoGuardrail.NAO_AVALIAVEL,
            motivo="Receita projetada não positiva.",
            preco_projetado=preco_alvo,
        )

    margem_projetada = (preco_alvo * (1 - comissao) - custo) * unidades
    rentabilidade_projetada = margem_projetada / receita_projetada

    if rentabilidade_projetada <= PISO_RENTABILIDADE:
        return ResultadoSimulacaoPreco(
            guardrail=guardrail,
            resultado=ResultadoGuardrail.BLOQUEADO,
            motivo=(
                f"Rentabilidade projetada de {rentabilidade_projetada:.2%} "
                f"não supera o piso de {PISO_RENTABILIDADE:.0%}."
            ),
            preco_projetado=preco_alvo,
            rentabilidade_projetada=rentabilidade_projetada,
            margem_projetada=margem_projetada,
        )

    return ResultadoSimulacaoPreco(
        guardrail=guardrail,
        resultado=ResultadoGuardrail.APROVADO,
        motivo=(
            f"Rentabilidade projetada de {rentabilidade_projetada:.2%} "
            f"supera o piso de {PISO_RENTABILIDADE:.0%}."
        ),
        preco_projetado=preco_alvo,
        rentabilidade_projetada=rentabilidade_projetada,
        margem_projetada=margem_projetada,
    )

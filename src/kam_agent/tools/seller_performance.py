"""Ferramentas determinísticas chamadas pelo grafo.

O identificador do seller vem do **estado da execução**, nunca do chamador,
do modelo ou do texto do usuário (guardrail #7). As assinaturas públicas não
expõem ``id_seller`` como parâmetro.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, timedelta
from typing import Any

from kam_agent.domain.enums import TipoGargalo
from kam_agent.domain.guardrails import classificar_gargalo
from kam_agent.domain.models import PerformanceSKU
from kam_agent.ports.seller_data import SellerDataPort

CHAVE_SELLER = "id_seller"


class SellerAusenteNoEstado(ValueError):
    """O estado não carrega o seller exigido pela ferramenta."""


def _seller_do_estado(estado: Mapping[str, Any]) -> str:
    id_seller = estado.get(CHAVE_SELLER)
    if not id_seller or not str(id_seller).strip():
        raise SellerAusenteNoEstado(
            "A ferramenta exige o identificador do seller no estado da execução."
        )
    return str(id_seller)


def resumir_performance(
    porta: SellerDataPort,
    estado: Mapping[str, Any],
    data_fim: date,
    janela_dias: int = 30,
) -> tuple[PerformanceSKU, ...]:
    """Lê a performance do seller registrado no estado da execução."""
    id_seller = _seller_do_estado(estado)
    data_inicio = data_fim - timedelta(days=janela_dias)
    return porta.ler_performance(id_seller, data_inicio, data_fim).registros


def classificar_registros(
    registros: tuple[PerformanceSKU, ...],
) -> dict[TipoGargalo, list[PerformanceSKU]]:
    """Agrupa registros por gargalo dominante."""
    por_gargalo: dict[TipoGargalo, list[PerformanceSKU]] = {}
    for registro in registros:
        gargalo = classificar_gargalo(registro)
        por_gargalo.setdefault(gargalo, []).append(registro)
    return por_gargalo


def contar_nao_avaliaveis(registros: tuple[PerformanceSKU, ...]) -> int:
    """Quantos registros não permitem análise no grão exigido."""
    return sum(1 for r in registros if not r.exige_sku_filho)


__all__ = [
    "SellerAusenteNoEstado",
    "classificar_registros",
    "contar_nao_avaliaveis",
    "resumir_performance",
]

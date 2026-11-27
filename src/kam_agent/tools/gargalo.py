"""Classificação de gargalo a partir de um registro de performance."""

from __future__ import annotations

from kam_agent.domain.enums import TipoGargalo
from kam_agent.domain.guardrails import classificar_gargalo
from kam_agent.domain.models import PerformanceSKU


def gargalo_do_sku(registro: PerformanceSKU) -> TipoGargalo:
    """Gargalo dominante, delegando às regras de guardrail.

    Registro de granularidade ``sku_pai`` resulta em ``NAO_AVALIAVEL`` quando a
    regra exige SKU filho.
    """
    return classificar_gargalo(registro)

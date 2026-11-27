"""Resolução de portas e configuração via dependências FastAPI (D10)."""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from kam_agent.adapters.factory import build_seller_data_port, build_session_memory_port
from kam_agent.config import Settings
from kam_agent.ports.seller_data import SellerDataPort
from kam_agent.ports.session_memory import SessionMemoryPort


@lru_cache(maxsize=1)
def obter_settings() -> Settings:
    """Configuração resolvida uma vez por processo."""
    return Settings()


def obter_porta_dados(
    settings: Settings = Depends(obter_settings),
) -> SellerDataPort:
    """Porta de dados conforme a configuração."""
    return build_seller_data_port(settings)


def obter_porta_memoria(
    settings: Settings = Depends(obter_settings),
) -> SessionMemoryPort:
    """Porta de memória conforme a configuração."""
    return build_session_memory_port(settings)

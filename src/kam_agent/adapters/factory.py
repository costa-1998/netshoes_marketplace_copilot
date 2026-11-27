"""Factory de portas a partir de ``Settings`` (D10).

As rotas nunca instanciam adapter diretamente.
"""

from __future__ import annotations

from kam_agent.adapters.bigquery_seller_data import BigQuerySellerAdapter
from kam_agent.adapters.in_memory_session import InMemorySessionAdapter
from kam_agent.adapters.mock_seller_data import CsvMockSellerAdapter
from kam_agent.config import Settings
from kam_agent.ports.seller_data import SellerDataPort
from kam_agent.ports.session_memory import SessionMemoryPort


def build_seller_data_port(settings: Settings) -> SellerDataPort:
    """Resolve a porta de dados conforme ``DW_BACKEND``."""
    if settings.dw_backend == "mock":
        return CsvMockSellerAdapter(
            caminho_dados=settings.mock_data_path,
            caminho_master=settings.mock_seller_master_path,
        )
    if settings.dw_backend == "bigquery":
        return BigQuerySellerAdapter(
            project_id=settings.bq_project_id,
            dataset=settings.bq_dataset,
            view=settings.bq_view_child_sku,
        )
    raise ValueError(
        f"DW_BACKEND inválido: {settings.dw_backend!r}. Valores aceitos: 'mock', 'bigquery'."
    )


def build_session_memory_port(settings: Settings) -> SessionMemoryPort:
    """Resolve a porta de memória conforme ``MEMORY_BACKEND``."""
    if settings.memory_backend == "memory":
        return InMemorySessionAdapter(ttl_segundos=settings.session_ttl_seconds)
    raise ValueError(
        f"MEMORY_BACKEND inválido: {settings.memory_backend!r}. Valores aceitos: 'memory'."
    )

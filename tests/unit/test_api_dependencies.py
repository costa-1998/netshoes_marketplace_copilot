"""Resolução de dependências por configuração (task 9.2)."""

from __future__ import annotations

from kam_agent.adapters.bigquery_seller_data import BigQuerySellerAdapter
from kam_agent.adapters.in_memory_session import InMemorySessionAdapter
from kam_agent.adapters.mock_seller_data import CsvMockSellerAdapter
from kam_agent.api.dependencies import (
    obter_porta_dados,
    obter_porta_memoria,
    obter_settings,
)
from kam_agent.config import Settings


def test_settings_e_cacheado() -> None:
    assert obter_settings() is obter_settings()


def test_porta_dados_mock() -> None:
    porta = obter_porta_dados(Settings(dw_backend="mock"))
    assert isinstance(porta, CsvMockSellerAdapter)


def test_porta_dados_bigquery() -> None:
    porta = obter_porta_dados(Settings(dw_backend="bigquery"))
    assert isinstance(porta, BigQuerySellerAdapter)


def test_porta_memoria() -> None:
    porta = obter_porta_memoria(Settings(memory_backend="memory"))
    assert isinstance(porta, InMemorySessionAdapter)

"""Factory de portas por configuração (task 6.3)."""

from __future__ import annotations

import pytest

from kam_agent.adapters.bigquery_seller_data import BigQuerySellerAdapter
from kam_agent.adapters.factory import build_seller_data_port, build_session_memory_port
from kam_agent.adapters.in_memory_session import InMemorySessionAdapter
from kam_agent.adapters.mock_seller_data import CsvMockSellerAdapter
from kam_agent.config import Settings


def test_mock_resolve_adapter_mock() -> None:
    porta = build_seller_data_port(Settings(dw_backend="mock"))
    assert isinstance(porta, CsvMockSellerAdapter)


def test_bigquery_resolve_adapter_bigquery() -> None:
    porta = build_seller_data_port(Settings(dw_backend="bigquery"))
    assert isinstance(porta, BigQuerySellerAdapter)


def test_memory_resolve_adapter_em_memoria() -> None:
    porta = build_session_memory_port(Settings(memory_backend="memory"))
    assert isinstance(porta, InMemorySessionAdapter)


def test_ttl_propagado_para_memoria() -> None:
    porta = build_session_memory_port(Settings(session_ttl_seconds=123))
    assert isinstance(porta, InMemorySessionAdapter)
    assert porta._ttl == 123


def test_backend_desconhecido_falha() -> None:
    settings = Settings.model_construct(dw_backend="postgres")
    with pytest.raises(ValueError) as exc:
        build_seller_data_port(settings)
    assert "mock" in str(exc.value) and "bigquery" in str(exc.value)


def test_memory_backend_desconhecido_falha() -> None:
    settings = Settings.model_construct(memory_backend="redis")
    with pytest.raises(ValueError):
        build_session_memory_port(settings)

"""Testes de configuração tipada (task 1.2)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from kam_agent.config import Settings


def test_backends_validos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DW_BACKEND", "mock")
    monkeypatch.setenv("MEMORY_BACKEND", "memory")
    settings = Settings()
    assert settings.dw_backend == "mock"
    assert settings.memory_backend == "memory"


def test_dw_backend_invalido_lista_aceitos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DW_BACKEND", "postgres")
    with pytest.raises(ValidationError) as exc:
        Settings()
    mensagem = str(exc.value)
    assert "mock" in mensagem
    assert "bigquery" in mensagem


def test_memory_backend_invalido_lista_aceitos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEMORY_BACKEND", "redis")
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert "memory" in str(exc.value)


def test_defaults_sem_variaveis_de_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOCK_DATA_PATH", raising=False)
    monkeypatch.delenv("MOCK_SELLER_MASTER_PATH", raising=False)
    settings = Settings()
    assert settings.mock_data_path.name == "seller_sku_sales.csv"
    assert settings.mock_seller_master_path.name == "seller_master.csv"


def test_ttl_deve_ser_positivo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SESSION_TTL_SECONDS", "0")
    with pytest.raises(ValidationError):
        Settings()

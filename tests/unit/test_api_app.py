"""Criação da aplicação e falha na configuração inválida (task 9.5)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from kam_agent.api.app import create_app
from kam_agent.api.dependencies import obter_settings
from kam_agent.config import Settings


def test_configuracao_invalida_falha_na_criacao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DW_BACKEND", "postgres")
    obter_settings.cache_clear()
    try:
        with pytest.raises(ValidationError):
            create_app()
    finally:
        obter_settings.cache_clear()


def test_configuracao_valida_responde_health() -> None:
    cliente = TestClient(create_app(Settings(dw_backend="mock")))
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["dw_backend"] == "mock"
    assert corpo["memory_backend"] == "memory"


def test_health_reporta_backends_em_uso() -> None:
    cliente = TestClient(create_app(Settings(dw_backend="mock")))
    corpo = cliente.get("/health").json()
    assert "dw_backend" in corpo and "memory_backend" in corpo

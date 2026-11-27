"""/health nomeia dependência indisponível (task 9.6)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from kam_agent.api.app import create_app
from kam_agent.config import Settings


def test_bigquery_reportado_como_indisponivel() -> None:
    cliente = TestClient(create_app(Settings(dw_backend="bigquery")))
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "degradado"
    assert any("bigquery" in dep.lower() for dep in corpo["dependencias_indisponiveis"])


def test_mock_reportado_como_saudavel() -> None:
    cliente = TestClient(create_app(Settings(dw_backend="mock")))
    corpo = cliente.get("/health").json()
    assert corpo["status"] == "ok"
    assert corpo["dependencias_indisponiveis"] == []

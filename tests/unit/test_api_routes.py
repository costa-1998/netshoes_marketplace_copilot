"""Rotas /health e /chat (task 9.3)."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from kam_agent.adapters.in_memory_session import InMemorySessionAdapter
from kam_agent.api.app import create_app
from kam_agent.api.dependencies import obter_porta_dados, obter_porta_memoria, obter_settings
from kam_agent.config import Settings
from kam_agent.ports.seller_data import DadosSeller


class _PortaFalsa:
    def __init__(self) -> None:
        self.sellers: list[str] = []

    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        self.sellers.append(id_seller)
        return DadosSeller(seller=None, registros=())

    def ler_seller(self, id_seller: str):
        return None


@pytest.fixture()
def cliente() -> TestClient:
    app = create_app(Settings(dw_backend="mock"))
    porta = _PortaFalsa()
    memoria = InMemorySessionAdapter(ttl_segundos=600)
    app.dependency_overrides[obter_porta_dados] = lambda: porta
    app.dependency_overrides[obter_porta_memoria] = lambda: memoria
    app.dependency_overrides[obter_settings] = lambda: Settings(dw_backend="mock")
    return TestClient(app)


def test_mensagem_valida_retorna_200(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/chat", json={"mensagem": "diagnostico"}, headers={"X-Seller-Id": "10024"}
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["id_seller"] == "10024"
    assert corpo["total_recomendacoes"] <= 3


def test_mensagem_vazia_retorna_422(cliente: TestClient) -> None:
    resposta = cliente.post("/chat", json={"mensagem": ""}, headers={"X-Seller-Id": "10024"})
    assert resposta.status_code == 422


def test_sem_sessao_nem_seller_erro_controlado(cliente: TestClient) -> None:
    resposta = cliente.post("/chat", json={"mensagem": "diagnostico"})
    assert resposta.status_code == 422
    assert "correlation_id" in resposta.json()


def test_id_seller_do_corpo_e_ignorado(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/chat",
        json={"mensagem": "diagnostico", "id_seller": "99999"},
        headers={"X-Seller-Id": "10024"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["id_seller"] == "10024"


def test_sessao_reaproveita_seller(cliente: TestClient) -> None:
    headers = {"X-Seller-Id": "10024", "X-Sessao": "s1"}
    primeira = cliente.post("/chat", json={"mensagem": "diagnostico"}, headers=headers)
    segunda = cliente.post("/chat", json={"mensagem": "diagnostico"}, headers={"X-Sessao": "s1"})
    assert primeira.json()["id_seller"] == segunda.json()["id_seller"] == "10024"

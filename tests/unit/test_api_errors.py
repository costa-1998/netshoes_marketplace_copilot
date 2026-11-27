"""Handler global de erros sem vazamento (task 9.4)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from kam_agent.api.app import create_app
from kam_agent.api.dependencies import obter_porta_dados, obter_settings
from kam_agent.config import Settings
from kam_agent.domain.exceptions import SellerNaoEncontrado


class _PortaQueFalha:
    def ler_performance(self, id_seller: str, data_inicio, data_fim):
        raise RuntimeError(
            "SELECT * FROM pdia0024.netshoes_kam_analytics.copiloto_seller_sku_diario "
            "falhou em /home/costa.cinthia/segredo/credenciais.json"
        )

    def ler_seller(self, id_seller: str):
        return None


@pytest.fixture()
def cliente_falha() -> TestClient:
    app = create_app(Settings(dw_backend="mock"))
    app.dependency_overrides[obter_porta_dados] = lambda: _PortaQueFalha()
    app.dependency_overrides[obter_settings] = lambda: Settings(dw_backend="mock")
    return TestClient(app, raise_server_exceptions=False)


def test_erro_de_dominio_vira_4xx() -> None:
    app = create_app(Settings(dw_backend="mock"))

    @app.get("/boom-dominio")
    def _boom() -> None:
        raise SellerNaoEncontrado("10024")

    cliente = TestClient(app)
    resposta = cliente.get("/boom-dominio")
    assert resposta.status_code == 422
    assert "10024" in resposta.json()["erro"]


def test_erro_inesperado_vira_500_sem_vazamento(cliente_falha: TestClient) -> None:
    resposta = cliente_falha.post(
        "/chat", json={"mensagem": "diagnostico"}, headers={"X-Seller-Id": "10024"}
    )
    assert resposta.status_code == 500
    corpo = resposta.text
    assert "correlation_id" in resposta.json()
    for proibido in ("SELECT", "copiloto_seller_sku_diario", "/home/", "credenciais"):
        assert proibido not in corpo
    assert "Traceback" not in corpo

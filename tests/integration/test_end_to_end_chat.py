"""Fluxo de ponta a ponta com as fixtures reais (task 10.1).

As fixtures estão no ``.gitignore``, então este teste se auto-pula quando elas
não existem (caso do CI).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kam_agent.api.app import create_app
from kam_agent.config import Settings

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
DADOS = FIXTURES / "seller_sku_sales.csv"
MASTER = FIXTURES / "seller_master.csv"

pytestmark = pytest.mark.skipif(
    not (DADOS.exists() and MASTER.exists()),
    reason="fixtures locais ausentes (ignoradas pelo .gitignore)",
)


@pytest.fixture()
def cliente() -> TestClient:
    settings = Settings(
        dw_backend="mock",
        mock_data_path=DADOS,
        mock_seller_master_path=MASTER,
    )
    return TestClient(create_app(settings))


def test_fluxo_completo_seller_10024(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/chat",
        json={"mensagem": "quero ver meu diagnostico"},
        headers={"X-Seller-Id": "10024"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["resposta"]
    assert corpo["id_seller"] == "10024"
    assert corpo["total_recomendacoes"] <= 3


def test_resposta_respeita_top3(cliente: TestClient) -> None:
    corpo = cliente.post(
        "/chat", json={"mensagem": "diagnostico"}, headers={"X-Seller-Id": "10024"}
    ).json()
    assert corpo["total_recomendacoes"] <= 3
    linhas_numeradas = [
        linha for linha in corpo["resposta"].splitlines() if linha[:2] in {"1.", "2.", "3."}
    ]
    assert len(linhas_numeradas) <= 3


def test_nenhuma_recomendacao_bloqueada_por_1p() -> None:
    """Recomendações devolvidas nunca carregam guardrail bloqueado, e nenhuma
    redução de preço é emitida para SKU filho com 1P ativo."""
    from datetime import date

    from kam_agent.adapters.mock_seller_data import CsvMockSellerAdapter
    from kam_agent.agents.graph import executar
    from kam_agent.domain.enums import ResultadoGuardrail, TipoRecomendacao

    porta = CsvMockSellerAdapter(caminho_dados=DADOS, caminho_master=MASTER)
    estado = executar(porta, "10024", "diagnostico", "cid", date(2026, 11, 27))

    recomendacoes = estado.get("recomendacoes") or ()
    assert recomendacoes, "esperava ao menos uma recomendação com a fixture real"

    for recomendacao in recomendacoes:
        assert all(g.resultado is ResultadoGuardrail.APROVADO for g in recomendacao.guardrails)

    registros_1p = {
        r.sku_filho
        for r in porta.ler_performance("10024", date(2026, 11, 1), date(2026, 11, 27))
        if r.tem_1p
    }
    reducoes_com_1p = [
        r
        for r in recomendacoes
        if r.tipo is TipoRecomendacao.REDUCAO_PRECO and r.sku_filho in registros_1p
    ]
    assert reducoes_com_1p == []


def test_seller_inexistente_nao_quebra(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/chat", json={"mensagem": "diagnostico"}, headers={"X-Seller-Id": "00000"}
    )
    assert resposta.status_code == 200
    assert resposta.json()["total_recomendacoes"] == 0

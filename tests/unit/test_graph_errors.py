"""Falhas no fluxo do grafo (task 8.4)."""

from __future__ import annotations

from datetime import date

from kam_agent.agents.graph import executar
from kam_agent.ports.seller_data import DadosSeller


class _PortaQueConta:
    def __init__(self) -> None:
        self.chamadas = 0

    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        self.chamadas += 1
        return DadosSeller(seller=None, registros=())

    def ler_seller(self, id_seller: str):
        return None


class _PortaQueFalha:
    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        raise RuntimeError("falha simulada na fonte")

    def ler_seller(self, id_seller: str):
        return None


def test_sem_seller_nao_consulta_dados() -> None:
    porta = _PortaQueConta()
    estado = executar(porta, "", "diagnostico", "c1", date(2026, 11, 27))
    assert porta.chamadas == 0
    assert estado.get("erro")


def test_sem_seller_devolve_resposta_controlada() -> None:
    estado = executar(_PortaQueConta(), "", "diagnostico", "c1", date(2026, 11, 27))
    assert estado.get("resposta")
    assert "seller" in estado["erro"].lower()


def test_erro_de_etapa_nao_propaga_excecao() -> None:
    estado = executar(_PortaQueFalha(), "10024", "diagnostico", "c1", date(2026, 11, 27))
    assert estado.get("erro")
    assert estado.get("correlation_id") == "c1"
    assert estado.get("resposta")


def test_erro_nao_vaza_detalhe_tecnico_na_resposta() -> None:
    estado = executar(_PortaQueFalha(), "10024", "diagnostico", "c1", date(2026, 11, 27))
    assert "falha simulada na fonte" not in (estado.get("resposta") or "")

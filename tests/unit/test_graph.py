"""Execução completa do grafo, sem rede (task 8.3)."""

from __future__ import annotations

import socket
from datetime import date

import pytest

from kam_agent.agents.graph import executar
from kam_agent.ports.seller_data import DadosSeller


class _PortaFalsa:
    """Porta em memória com um registro de SKU filho em ruptura de Curva A."""

    def __init__(self, registros: tuple = ()) -> None:
        self._registros = registros
        self.chamadas = 0

    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        self.chamadas += 1
        return DadosSeller(seller=None, registros=self._registros)

    def ler_seller(self, id_seller: str):
        return None


def _registro_ruptura():
    from kam_agent.domain.models import PerformanceSKU

    return PerformanceSKU(
        data=date(2026, 11, 27),
        id_seller="10024",
        sku_pai="P1",
        sku_filho="F1",
        categoria_curva="A",
        cobertura=1.0,
        tem_1p=False,
        receita_faturada=1000.0,
    )


def test_execucao_completa_devolve_resposta(monkeypatch: pytest.MonkeyPatch) -> None:
    def _proibido(*args: object, **kwargs: object):
        raise AssertionError("execução offline não pode abrir conexão de rede")

    monkeypatch.setattr(socket.socket, "connect", _proibido)

    estado = executar(
        porta=_PortaFalsa((_registro_ruptura(),)),
        id_seller="10024",
        mensagem="diagnostico",
        correlation_id="c1",
        data_referencia=date(2026, 11, 27),
    )
    assert estado.get("erro") is None
    assert estado.get("resposta")
    assert estado.get("especialista") == "diagnostico"


def test_execucao_consulta_a_porta() -> None:
    porta = _PortaFalsa((_registro_ruptura(),))
    executar(porta, "10024", "diagnostico", "c1", date(2026, 11, 27))
    assert porta.chamadas == 1

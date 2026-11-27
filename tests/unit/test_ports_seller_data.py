"""Contrato de ``SellerDataPort`` (task 4.1)."""

from __future__ import annotations

from datetime import date

from kam_agent.ports.seller_data import DadosSeller, SellerDataPort


class _StubConforme:
    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        return DadosSeller(seller=None, registros=())

    def ler_seller(self, id_seller: str):
        return None


class _StubIncompleto:
    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        return DadosSeller(seller=None, registros=())


def test_stub_conforme_satisfaz_protocolo() -> None:
    assert isinstance(_StubConforme(), SellerDataPort)


def test_objeto_incompleto_nao_satisfaz() -> None:
    assert not isinstance(_StubIncompleto(), SellerDataPort)


def test_objeto_arbitrario_nao_satisfaz() -> None:
    assert not isinstance(object(), SellerDataPort)


def test_dto_e_iteravel_e_contavel() -> None:
    dados = DadosSeller(seller=None, registros=())
    assert len(dados) == 0
    assert list(dados) == []

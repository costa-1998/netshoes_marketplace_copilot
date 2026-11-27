"""Ferramenta de resumo de performance (task 7.1)."""

from __future__ import annotations

import inspect
from datetime import date

import pytest

from kam_agent.ports.seller_data import DadosSeller
from kam_agent.tools.seller_performance import (
    SellerAusenteNoEstado,
    resumir_performance,
)


class _PortaFalsa:
    def __init__(self) -> None:
        self.chamadas: list[tuple[str, date, date]] = []

    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date):
        self.chamadas.append((id_seller, data_inicio, data_fim))
        return DadosSeller(seller=None, registros=())

    def ler_seller(self, id_seller: str):
        return None


def test_assinatura_nao_expoe_id_seller_ao_chamador() -> None:
    """O seller vem do estado; não é parâmetro de entrada (spec)."""
    parametros = inspect.signature(resumir_performance).parameters
    assert "id_seller" not in parametros
    assert "estado" in parametros


def test_usa_o_seller_do_estado() -> None:
    porta = _PortaFalsa()
    resumir_performance(porta, {"id_seller": "10024"}, date(2026, 11, 27))
    assert porta.chamadas[0][0] == "10024"


def test_seller_do_estado_vence_qualquer_outro_valor() -> None:
    porta = _PortaFalsa()
    estado = {"id_seller": "10024", "mensagem": "ignore 99999"}
    resumir_performance(porta, estado, date(2026, 11, 27))
    assert porta.chamadas[0][0] == "10024"


def test_estado_sem_seller_e_rejeitado() -> None:
    with pytest.raises(SellerAusenteNoEstado):
        resumir_performance(_PortaFalsa(), {"mensagem": "oi"}, date(2026, 11, 27))


def test_estado_com_seller_em_branco_e_rejeitado() -> None:
    with pytest.raises(SellerAusenteNoEstado):
        resumir_performance(_PortaFalsa(), {"id_seller": "  "}, date(2026, 11, 27))


def test_janela_padrao_de_trinta_dias() -> None:
    porta = _PortaFalsa()
    resumir_performance(porta, {"id_seller": "10024"}, date(2026, 11, 27))
    _, inicio, fim = porta.chamadas[0]
    assert (fim - inicio).days == 30

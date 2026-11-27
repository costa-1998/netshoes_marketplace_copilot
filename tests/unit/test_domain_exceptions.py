"""Testes das exceções de domínio (task 2.3)."""

from __future__ import annotations

from kam_agent.domain.exceptions import (
    DomainError,
    GranularidadeInsuficiente,
    SellerNaoEncontrado,
    SimulacaoInvalida,
)


def test_todas_herdam_de_domain_error() -> None:
    for exc in (SellerNaoEncontrado, GranularidadeInsuficiente, SimulacaoInvalida):
        assert issubclass(exc, DomainError)


def test_mensagens_legiveis() -> None:
    assert "10024" in str(SellerNaoEncontrado("10024"))
    assert "SKU" in str(GranularidadeInsuficiente("P1"))
    assert "rentabilidade" in str(SimulacaoInvalida("rentabilidade abaixo do piso"))


def test_atributos_preservados() -> None:
    erro = SellerNaoEncontrado("10024")
    assert erro.id_seller == "10024"
    assert SimulacaoInvalida("motivo").motivo == "motivo"

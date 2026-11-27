"""Modelos de requisição e resposta do chat (task 9.1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from kam_agent.api.schemas import RequisicaoChat


def test_mensagem_valida_aceita() -> None:
    assert RequisicaoChat(mensagem="oi").mensagem == "oi"


def test_mensagem_vazia_rejeitada() -> None:
    with pytest.raises(ValidationError):
        RequisicaoChat(mensagem="")


def test_mensagem_so_espacos_rejeitada() -> None:
    with pytest.raises(ValidationError):
        RequisicaoChat(mensagem="   ")


def test_mensagem_normalizada() -> None:
    assert RequisicaoChat(mensagem="  oi  ").mensagem == "oi"


def test_id_seller_no_corpo_nao_e_propagado() -> None:
    requisicao = RequisicaoChat.model_validate({"mensagem": "oi", "id_seller": "99999"})
    assert not hasattr(requisicao, "id_seller")
    assert "id_seller" not in requisicao.model_dump()

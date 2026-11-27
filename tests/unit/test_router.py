"""Roteamento determinístico (task 8.2)."""

from __future__ import annotations

import pytest

from kam_agent.agents.router import ESPECIALISTA_PADRAO, rotear


@pytest.mark.parametrize(
    ("mensagem", "esperado"),
    [
        ("me ajuda com o diagnostico", "diagnostico"),
        ("meu preco esta alto", "preco"),
        ("estou com ruptura de estoque", "estoque"),
        ("muita gente abandona o checkout", "funil"),
    ],
)
def test_intencao_suportada(mensagem: str, esperado: str) -> None:
    assert rotear(mensagem) == esperado


def test_intencao_nao_reconhecida_usa_padrao() -> None:
    assert rotear("bom dia, tudo bem?") == ESPECIALISTA_PADRAO


def test_determinismo() -> None:
    mensagem = "meu preco e meu estoque"
    assert len({rotear(mensagem) for _ in range(20)}) == 1


def test_case_insensitive() -> None:
    assert rotear("DIAGNOSTICO") == rotear("diagnostico")


def test_mensagem_vazia_usa_padrao() -> None:
    assert rotear("") == ESPECIALISTA_PADRAO

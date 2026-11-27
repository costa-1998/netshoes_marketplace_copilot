"""Estado do grafo (task 8.1)."""

from __future__ import annotations

from kam_agent.agents.state import CAMPOS_OBRIGATORIOS, EstadoAgente, validar_estado


def test_estado_minimo_construivel() -> None:
    estado: EstadoAgente = {
        "id_seller": "10024",
        "mensagem": "oi",
        "correlation_id": "c1",
    }
    assert validar_estado(estado) == []


def test_seller_obrigatorio() -> None:
    estado: EstadoAgente = {"id_seller": "", "mensagem": "oi", "correlation_id": "c1"}
    assert "id_seller" in validar_estado(estado)


def test_campos_obrigatorios_declarados() -> None:
    assert CAMPOS_OBRIGATORIOS == ("id_seller", "mensagem", "correlation_id")


def test_mensagem_obrigatoria() -> None:
    estado: EstadoAgente = {"id_seller": "1", "mensagem": "", "correlation_id": "c"}
    assert validar_estado(estado) == ["mensagem"]

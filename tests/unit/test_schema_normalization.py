"""Normalização de valores do mapeamento (task 5.2)."""

from __future__ import annotations

import pytest

from kam_agent.adapters.schema_mapping import (
    converter_registro,
    normalizar_booleano,
    normalizar_numero,
    normalizar_texto,
)


def test_residuo_de_ponto_flutuante_vira_zero() -> None:
    assert normalizar_numero("1.1102230246251565e-16") == 0.0


def test_residuo_negativo_vira_zero() -> None:
    assert normalizar_numero(-1e-12) == 0.0


def test_valor_normal_preservado() -> None:
    assert normalizar_numero("349.9") == pytest.approx(349.9)


def test_texto_vazio_vira_none() -> None:
    assert normalizar_texto("   ") is None
    assert normalizar_texto("") is None


def test_texto_preservado() -> None:
    assert normalizar_texto(" Calçados ") == "Calçados"


def test_booleano_textual() -> None:
    assert normalizar_booleano("true") is True
    assert normalizar_booleano("False") is False
    assert normalizar_booleano("") is None
    assert normalizar_booleano("talvez") is None


def test_unidades_vendidas_zero_preservado() -> None:
    convertidos = converter_registro({"unidades_vendidas": "0"}, "fixture")
    assert convertidos["unidades_vendidas"] == 0.0


def test_zero_e_ausencia_apenas_onde_declarado() -> None:
    # vmd na view tem zero_e_ausencia=True.
    convertidos = converter_registro({"vmd_com_estoque_fim_dia": "0"}, "view")
    assert convertidos["vmd"] is None


def test_preco_1p_vazio_na_fixture() -> None:
    convertidos = converter_registro({"preco_1p": ""}, "fixture")
    assert convertidos["preco_1p"] is None

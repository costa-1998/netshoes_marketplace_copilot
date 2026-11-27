"""Tabela de mapeamento schema → domínio (task 5.1)."""

from __future__ import annotations

import pytest

from kam_agent.adapters.schema_mapping import (
    MAPEAMENTO,
    campos_sem_origem,
    converter_registro,
    entradas_por_origem,
)


def test_toda_entrada_tem_origem_valida() -> None:
    for entrada in MAPEAMENTO:
        assert entrada.origem in {"fixture", "view"}


def test_toda_entrada_tem_coluna_ou_derivacao() -> None:
    for entrada in MAPEAMENTO:
        assert entrada.coluna is not None or entrada.derivacao is not None, entrada


def test_dois_vocabularios_cobertos() -> None:
    colunas_fixture = {e.coluna for e in entradas_por_origem("fixture")}
    colunas_view = {e.coluna for e in entradas_por_origem("view")}
    assert "preco_por" in colunas_fixture
    assert "tem_1p" in colunas_fixture
    assert "preco_por_fim_dia" in colunas_view
    assert "flag_1p_ativo_sku" in colunas_view


def test_derivacao_de_winner_avg_price_na_view() -> None:
    convertidos = converter_registro({"menor_preco_por_sku_dia": "349.9"}, "view")
    assert convertidos["winner_avg_price"] == pytest.approx(349.9)


def test_campo_sem_origem_permanece_ausente() -> None:
    # curva_abc não existe na view; categoria_curva não é mapeada para view.
    convertidos = converter_registro({"preco_por_fim_dia": "10"}, "view")
    assert "categoria_curva" not in convertidos
    assert "categoria_curva" in campos_sem_origem("view")


def test_campos_sem_origem_fixture_nao_incluem_metricas_conhecidas() -> None:
    sem_origem = campos_sem_origem("fixture")
    for campo in ("preco_por", "delta_preco", "tem_1p", "buybox_win_rate"):
        assert campo not in sem_origem


def test_conversao_fixture_traduz_linha_completa() -> None:
    linha = {
        "data": "2026-11-14",
        "id_seller": "10024",
        "sku_pai": "P1",
        "sku_filho": "F1",
        "preco_por": "349.9",
        "tem_1p": "false",
        "buybox_win_rate": "0.88",
    }
    convertidos = converter_registro(linha, "fixture")
    assert convertidos["preco_por"] == pytest.approx(349.9)
    assert convertidos["tem_1p"] is False
    assert convertidos["buybox_win_rate"] == pytest.approx(0.88)
    assert convertidos["sku_filho"] == "F1"

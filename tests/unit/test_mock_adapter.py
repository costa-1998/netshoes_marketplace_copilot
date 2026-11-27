"""Adapter mock: filtro por seller e janela (task 5.3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from kam_agent.adapters.mock_seller_data import CsvMockSellerAdapter

CABECALHO = (
    "data,id_seller,sku_pai,sku_filho,nome_produto,categoria_do_produto,"
    "categoria_curva,vmd,unidades_vendidas,receita_captada,receita_faturada,"
    "valor_de_comissao,preco_de,preco_por,preco_1p,delta_preco,margem,estoque,"
    "cobertura,sessoes,cliques,adicao_ao_carrinho,adicao_de_pagamento,"
    "adicao_de_informacoes_de_envio,compras_faturadas,cancelamentos,"
    "prazo_medio_envio,delta_prazo,custo_frete,tem_1p,buybox_win_rate,"
    "winner_avg_price,winner_avg_prazo,rentabilidade,taxa_conversao,"
    "percentual_de_comissao\n"
)

MASTER = (
    "id_seller,nome_seller,nota_reputacao,contato_nome,contato_telefone,"
    "contato_email,rentabilidade,taxa_conversao,percentual_de_comissao\n"
    "10024,Mary Jane,4.8,M,5511,m@x.com,0.29,0.019,0.2\n"
)


def _linha(data: str, seller: str, sku: str, preco: str = "100") -> str:
    return (
        f"{data},{seller},P1,{sku},Produto,Calçados,A,5,2,200,180,36,110,"
        f"{preco},,0,80,10,5,100,50,40,35,30,2,0,2,0,10,false,0.8,100,2,0.3,0.02,0.2\n"
    )


@pytest.fixture()
def adapter(tmp_path: Path) -> CsvMockSellerAdapter:
    dados = tmp_path / "dados.csv"
    dados.write_text(
        CABECALHO
        + _linha("2026-11-14", "10024", "F1")
        + _linha("2026-11-15", "10024", "F1")
        + _linha("2026-11-16", "10024", "F2")
        + _linha("2026-11-14", "99999", "F9"),
        encoding="utf-8",
    )
    master = tmp_path / "master.csv"
    master.write_text(MASTER, encoding="utf-8")
    return CsvMockSellerAdapter(caminho_dados=dados, caminho_master=master)


def test_filtra_por_seller_e_janela(adapter: CsvMockSellerAdapter) -> None:
    dados = adapter.ler_performance("10024", date(2026, 11, 14), date(2026, 11, 15))
    assert len(dados.registros) == 2
    assert {r.data for r in dados.registros} == {date(2026, 11, 14), date(2026, 11, 15)}
    assert all(r.id_seller == "10024" for r in dados.registros)


def test_seller_inexistente_devolve_vazio(adapter: CsvMockSellerAdapter) -> None:
    dados = adapter.ler_performance("00000", date(2026, 11, 1), date(2026, 11, 30))
    assert dados.registros == ()


def test_janela_inclusiva(adapter: CsvMockSellerAdapter) -> None:
    dados = adapter.ler_performance("10024", date(2026, 11, 16), date(2026, 11, 16))
    assert len(dados.registros) == 1
    assert dados.registros[0].sku_filho == "F2"


def test_granularidade_sku_filho_quando_presente(adapter: CsvMockSellerAdapter) -> None:
    dados = adapter.ler_performance("10024", date(2026, 11, 14), date(2026, 11, 16))
    assert all(r.exige_sku_filho for r in dados.registros)


def test_master_carregado(adapter: CsvMockSellerAdapter) -> None:
    dados = adapter.ler_performance("10024", date(2026, 11, 14), date(2026, 11, 14))
    assert dados.seller is not None
    assert dados.seller.nome_seller == "Mary Jane"

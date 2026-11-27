"""Guarda contra contaminação multi-tenant (task 5.5)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

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
)


def _linha(data: str, seller: str, sku: str) -> str:
    return (
        f"{data},{seller},P1,{sku},Produto,Calçados,A,5,2,200,180,36,110,"
        f"100,,0,80,10,5,100,50,40,35,30,2,0,2,0,10,false,0.8,100,2,0.3,0.02,0.2\n"
    )


def _adapter(tmp_path: Path) -> CsvMockSellerAdapter:
    dados = tmp_path / "dados.csv"
    dados.write_text(
        CABECALHO
        + _linha("2026-11-14", "10024", "F1")
        + _linha("2026-11-14", "99999", "F1"),  # mesmo SKU filho de outro seller
        encoding="utf-8",
    )
    master = tmp_path / "master.csv"
    master.write_text(MASTER, encoding="utf-8")
    return CsvMockSellerAdapter(caminho_dados=dados, caminho_master=master)


def test_registro_de_outro_seller_nao_aparece(tmp_path: Path) -> None:
    dados = _adapter(tmp_path).ler_performance("10024", date(2026, 11, 14), date(2026, 11, 14))
    assert len(dados.registros) == 1
    assert dados.registros[0].id_seller == "10024"


def test_inconsistencia_registrada(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    adapter.ler_performance("10024", date(2026, 11, 14), date(2026, 11, 14))
    assert len(adapter.inconsistencias) == 1
    assert "99999" in adapter.inconsistencias[0]


def test_inconsistencia_logada(tmp_path: Path, caplog: object) -> None:
    adapter = _adapter(tmp_path)
    import logging as _logging

    with caplog.at_level(_logging.WARNING):  # type: ignore[attr-defined]
        adapter.ler_performance("10024", date(2026, 11, 14), date(2026, 11, 14))
    assert any(
        "multi-tenant" in registro.message.lower()  # type: ignore[attr-defined]
        for registro in caplog.records  # type: ignore[attr-defined]
    )


def test_seller_legitimo_sem_ruido(tmp_path: Path) -> None:
    """Um SKU distinto de outro seller não é contaminação."""
    dados = tmp_path / "dados.csv"
    dados.write_text(
        CABECALHO + _linha("2026-11-14", "10024", "F1") + _linha("2026-11-14", "99999", "F9"),
        encoding="utf-8",
    )
    master = tmp_path / "master.csv"
    master.write_text(MASTER, encoding="utf-8")
    adapter = CsvMockSellerAdapter(caminho_dados=dados, caminho_master=master)
    adapter.ler_performance("10024", date(2026, 11, 14), date(2026, 11, 14))
    assert adapter.inconsistencias == []

"""Rejeição de leitura inválida sem tocar o arquivo (task 5.4)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from kam_agent.adapters.mock_seller_data import CsvMockSellerAdapter, SellerInvalido


def _adapter_inexistente(tmp_path: Path) -> CsvMockSellerAdapter:
    """Aponta para arquivos que não existem: qualquer leitura falharia com OSError."""
    return CsvMockSellerAdapter(
        caminho_dados=tmp_path / "nao_existe.csv",
        caminho_master=tmp_path / "nao_existe_master.csv",
    )


def test_leitura_sem_seller_rejeitada_antes_de_abrir_arquivo(tmp_path: Path) -> None:
    adapter = _adapter_inexistente(tmp_path)
    with pytest.raises(SellerInvalido):
        adapter.ler_performance("", date(2026, 11, 1), date(2026, 11, 30))


def test_leitura_com_seller_em_branco_rejeitada(tmp_path: Path) -> None:
    adapter = _adapter_inexistente(tmp_path)
    with pytest.raises(SellerInvalido):
        adapter.ler_performance("   ", date(2026, 11, 1), date(2026, 11, 30))


def test_janela_invertida_rejeitada_antes_de_abrir_arquivo(tmp_path: Path) -> None:
    adapter = _adapter_inexistente(tmp_path)
    with pytest.raises(SellerInvalido):
        adapter.ler_performance("10024", date(2026, 11, 30), date(2026, 11, 1))


def test_erro_nao_e_file_not_found(tmp_path: Path) -> None:
    adapter = _adapter_inexistente(tmp_path)
    with pytest.raises(SellerInvalido) as exc:
        adapter.ler_performance("", date(2026, 11, 1), date(2026, 11, 30))
    assert not isinstance(exc.value, FileNotFoundError)

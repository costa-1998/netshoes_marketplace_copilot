"""Adapter BigQuery falha alto (task 6.1)."""

from __future__ import annotations

from datetime import date

import pytest

from kam_agent.adapters.bigquery_seller_data import BigQuerySellerAdapter
from kam_agent.ports.seller_data import SellerDataPort


def _adapter() -> BigQuerySellerAdapter:
    return BigQuerySellerAdapter(project_id="p", dataset="d", view="v")


def test_satisfaz_a_porta() -> None:
    assert isinstance(_adapter(), SellerDataPort)


def test_leitura_levanta_not_implemented() -> None:
    with pytest.raises(NotImplementedError) as exc:
        _adapter().ler_performance("10024", date(2026, 11, 1), date(2026, 11, 30))
    assert str(exc.value).strip()
    assert "BigQuery" in str(exc.value)


def test_leitura_de_seller_levanta_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        _adapter().ler_seller("10024")

"""Adapter BigQuery — stub explícito que falha alto (D6).

Devolver uma coleção vazia seria indistinguível de "seller sem dados" e
mascararia a ausência de implementação. A mensagem nomeia a limitação.
"""

from __future__ import annotations

from datetime import date

from kam_agent.domain.models import SellerMaster
from kam_agent.ports.seller_data import DadosSeller

MENSAGEM_NAO_IMPLEMENTADO = (
    "BigQuerySellerAdapter não está implementado nesta change "
    "(001-core-contracts-and-skeleton): a execução de SQL na view "
    "copiloto_seller_sku_diario é escopo de uma change futura. "
    "Use DW_BACKEND=mock para execução offline."
)


class BigQuerySellerAdapter:
    """Satisfaz ``SellerDataPort``, mas toda leitura levanta erro."""

    def __init__(self, project_id: str, dataset: str, view: str) -> None:
        self.project_id = project_id
        self.dataset = dataset
        self.view = view

    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date) -> DadosSeller:
        raise NotImplementedError(MENSAGEM_NAO_IMPLEMENTADO)

    def ler_seller(self, id_seller: str) -> SellerMaster | None:
        raise NotImplementedError(MENSAGEM_NAO_IMPLEMENTADO)

"""Exceções de domínio do copiloto KAM.

Todas herdam de :class:`DomainError`, que a camada de API mapeia para 4xx
sem vazar detalhe interno (D11).
"""

from __future__ import annotations


class DomainError(Exception):
    """Erro de regra de negócio, seguro para expor ao cliente."""


class SellerNaoEncontrado(DomainError):
    """O seller solicitado não existe na fonte de dados."""

    def __init__(self, id_seller: str) -> None:
        self.id_seller = id_seller
        super().__init__(f"Seller '{id_seller}' não encontrado.")


class GranularidadeInsuficiente(DomainError):
    """A análise exige SKU filho, mas o registro é de SKU pai."""

    def __init__(self, sku_pai: str) -> None:
        self.sku_pai = sku_pai
        super().__init__(f"Registro do SKU pai '{sku_pai}' não possui granularidade de SKU filho.")


class SimulacaoInvalida(DomainError):
    """A simulação de preço viola uma regra de negócio ou carece de dado."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(f"Simulação inválida: {motivo}")
